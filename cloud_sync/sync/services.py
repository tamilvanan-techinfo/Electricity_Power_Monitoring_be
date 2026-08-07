from asgiref.sync import sync_to_async
from django.db.models import F


@sync_to_async
def save_monitor_data(data):
    # Import after Django is fully initialized
    from core.models import ParticipentCycle, PowerMonitor,Cycle

    try:
        controller_no = data.get("controller_no")
        cycle = Cycle.objects.get(controller_no=controller_no)
        allocation = ParticipentCycle.objects.get(cycle=cycle)

        current_voltage = float(data.get("voltage", 0.0))
        current_amperage = float(data.get("amperage", 0.0))
        current_power = float(data.get("power", 0.0))

        allocation.voltage = current_voltage
        allocation.amperage = current_amperage
        allocation.power = current_power

        allocation.total_voltage = F("total_voltage") + current_voltage
        allocation.total_amperage = F("total_amperage") + current_amperage
        allocation.total_power = F("total_power") + current_power

        allocation.save()
        allocation.refresh_from_db()

        PowerMonitor.objects.create(
            participent=allocation,
            current_power=current_power,
            current_voltage=current_voltage,
            current_amperage=current_amperage,
            total_power=allocation.total_power,
            total_voltage=allocation.total_voltage,
            total_amperage=allocation.total_amperage,
        )

    except ParticipentCycle.DoesNotExist:
        print(f"Cycle {controller_no} not found.")