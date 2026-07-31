import asyncio
import json
from datetime import timedelta
from collections import defaultdict

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from .models import PowerMonitor, ActiveParticipent, Cycle


class PowerMonitorConsumer(AsyncWebsocketConsumer):

    DEFAULT_MINUTES = 2
    MIN_MINUTES = 1
    MAX_MINUTES = 24 * 60  # safety cap

    POLL_INTERVAL_SECONDS = 5

    ROLE_ADMIN = "admin"
    ROLE_CLIENT = "client"
    VALID_ROLES = {ROLE_ADMIN, ROLE_CLIENT}

    async def connect(self):
        self.group_name = "power_monitor"

        self.role = self.get_role_from_route()

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

        self.running = True
        self.task = asyncio.create_task(self.stream_data())

    # ---------- role from the URL path ----------

    def get_role_from_route(self):
        role = self.scope.get("url_route", {}).get("kwargs", {}).get("role")

        if role:
            role = role.strip().lower()

        if role not in self.VALID_ROLES:
            return self.ROLE_ADMIN

        return role

    # ---------- pull live config from ActiveParticipent ----------

    @database_sync_to_async
    def get_active_config(self):
        """
        Reads the *current* ActiveParticipent row (the one you use to drive
        the live view) and converts it into:
            minutes    -> int, derived from the TimeField (00:10:00 -> 10)
            cycle_nos  -> list[str] of cycle_no's tied to that row via the
                          ManyToMany, or None if none are attached (meaning
                          "all cycles")

        This is called on every poll tick (not just once at connect) so
        that if you update ActiveParticipent while the socket is open, the
        rolling window and cycle filter update live without a reconnect.
        """
        active = (
            ActiveParticipent.objects
            .prefetch_related("cycle")
            .order_by("-id")
            .first()
        )

        if active is None:
            return self.DEFAULT_MINUTES, None

        td = active.time_duration  # datetime.time
        minutes = td.hour * 60 + td.minute + (1 if td.second >= 30 else 0)
        minutes = self.clamp_minutes(minutes if minutes > 0 else self.DEFAULT_MINUTES)

        cycle_nos = list(active.cycle.values_list("cycle_no", flat=True))
        cycle_nos = cycle_nos or None

        return minutes, cycle_nos

    def clamp_minutes(self, minutes):
        if minutes < self.MIN_MINUTES:
            return self.MIN_MINUTES
        if minutes > self.MAX_MINUTES:
            return self.MAX_MINUTES
        return minutes

    # ---------- lifecycle ----------

    async def disconnect(self, close_code):
        self.running = False

        if hasattr(self, "task"):
            self.task.cancel()

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Admin-only. Lets the admin drawer push a new time_duration (minutes)
        and/or cycle selection, which is written straight to the
        ActiveParticipent row that drives the live window/filter for
        everyone (admins and clients both read it on the next poll tick).

        Expected payload:
            {"minutes": 10, "cycles": ["1", "2"]}
            {"minutes": 10}                # cycles left untouched
            {"cycles": []}                 # clears cycle filter -> all cycles
        """
        if self.role != self.ROLE_ADMIN:
            return

        if not text_data:
            return

        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"type": "error", "message": "invalid_json"}))
            return

        minutes = payload.get("minutes")
        cycles = payload.get("cycles")

        try:
            active = await self.update_active_config(minutes, cycles)
        except ValueError as exc:
            await self.send(text_data=json.dumps({"type": "error", "message": str(exc)}))
            return

        await self.send(
            text_data=json.dumps(
                {
                    "type": "config_updated",
                    "minutes": active["minutes"],
                    "cycles": active["cycles"],
                }
            )
        )

    @database_sync_to_async
    def update_active_config(self, minutes, cycles):
        """
        Writes to the single ActiveParticipent row (created if it doesn't
        exist yet). `minutes` becomes the TimeField time_duration; `cycles`
        (a list of cycle_no strings) replaces the M2M set. Either argument
        can be omitted/None to leave that piece untouched.
        """
        from datetime import time as time_cls

        active = ActiveParticipent.objects.order_by("-id").first()
        if active is None:
            active = ActiveParticipent(time_duration=time_cls(0, self.DEFAULT_MINUTES, 0))
            active.save()

        if minutes is not None:
            try:
                minutes_int = self.clamp_minutes(int(minutes))
            except (TypeError, ValueError):
                raise ValueError("minutes must be an integer")
            active.time_duration = time_cls(minutes_int // 60, minutes_int % 60, 0)
            active.save(update_fields=["time_duration"])

        if cycles is not None:
            if not isinstance(cycles, list):
                raise ValueError("cycles must be a list")
            cycle_qs = Cycle.objects.filter(cycle_no__in=[str(c) for c in cycles])
            active.cycle.set(cycle_qs)

        td = active.time_duration
        return {
            "minutes": td.hour * 60 + td.minute,
            "cycles": list(active.cycle.values_list("cycle_no", flat=True)),
        }

    # ---------- streaming loop ----------

    async def stream_data(self):
        if self.role == self.ROLE_ADMIN:
            # Admins don't receive the live stream — only clients do.
            return

        try:
            while self.running:
                minutes, cycle_nos = await self.get_active_config()

                data = await self.get_chart_data(minutes, cycle_nos)

                await self.send(
                    text_data=json.dumps(
                        {
                            "type": "trend",
                            "timestamp": asyncio.get_running_loop().time(),
                            "window_minutes": minutes,
                            "cycles": cycle_nos,
                            "generated_at": timezone.now().isoformat(),
                            "series": data,
                        }
                    )
                )

                await asyncio.sleep(self.POLL_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            pass

    # ---------- data query ----------

    @database_sync_to_async
    def get_chart_data(self, minutes, cycle_nos):
        """
        Returns EVERY reading for each participant within the rolling
        window [now - minutes, now].

        Because `timezone.now()` is evaluated fresh on every call, and
        `minutes`/`cycle_nos` are re-read from ActiveParticipent on every
        tick in stream_data(), both the window and the cycle filter track
        live changes: at 9:40 with a 10-min ActiveParticipent row you get
        [9:30, 9:40]; at 9:41 you get [9:31, 9:41]; if the row's
        time_duration or cycle set changes, the next tick reflects that.
        """
        now = timezone.now()

        readings = PowerMonitor.objects.select_related(
            "participent",
            "participent__participent",   # ParticipentCycle -> Participent
            "participent__cycle",         # ParticipentCycle -> Cycle
        ).only(
            "current_voltage",
            "current_amperage",
            "current_power",
            "updated_at",
            "participent_id",
            "participent__cycle__cycle_no",
            "participent__participent__name",
        ).order_by("participent_id", "updated_at")

        if minutes is not None:
            cutoff = now - timedelta(minutes=minutes)
            readings = readings.filter(updated_at__gte=cutoff, updated_at__lte=now)

        if cycle_nos:
            readings = readings.filter(participent__cycle__cycle_no__in=cycle_nos)

        grouped = defaultdict(lambda: {"participant_name": None, "cycle_no": None, "points": []})

        for item in readings:
            key = item.participent_id
            bucket = grouped[key]
            bucket["participant_name"] = item.participent.participent.name
            bucket["cycle_no"] = item.participent.cycle.cycle_no
            bucket["points"].append({
                "time": item.updated_at.isoformat(),
                "power": item.current_power,
                "voltage": item.current_voltage,
                "current": item.current_amperage,
            })

        return [
            {
                "participant_cycle_id": key,
                "participant_name": bucket["participant_name"],
                "cycle_no": bucket["cycle_no"],
                "points": bucket["points"],
            }
            for key, bucket in grouped.items()
        ]