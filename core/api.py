import random

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ParticipentCycle


from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UpdateReadingAPIView(APIView):

    def post(self, request):
        cycle_id = request.data.get("cycle_id")
        voltage = request.data.get("voltage")
        amperage = request.data.get("amperage")
        power = request.data.get("power")

        try:
            allocation = ParticipentCycle.objects.get(pk=cycle_id)

            # convert to floats (protect against None/string)
            current_voltage = float(voltage or 0.0)
            current_amperage = float(amperage or 0.0)
            current_power = float(power or 0.0)

            # latest readings
            allocation.voltage = current_voltage
            allocation.amperage = current_amperage
            allocation.power = current_power

            # accumulate totals in DB:
            # total_x = total_x + current_x
            allocation.total_voltage = F('total_voltage') + current_voltage
            allocation.total_amperage = F('total_amperage') + current_amperage
            allocation.total_power = F('total_power') + current_power

            allocation.save()

            # reload actual numeric totals after F() updates
            allocation.refresh_from_db()  # [web:36][web:44][web:47]

            return Response(
                {
                    "status": "success",
                    "cycle": allocation.cycle.cycle_no,
                    "voltage": allocation.voltage,           # latest voltage
                    "amperage": allocation.amperage,         # latest amp
                    "power": allocation.power,               # latest power
                    "total_voltage": allocation.total_voltage,
                    "total_amperage": allocation.total_amperage,
                    "total_power": allocation.total_power,
                },
                status=status.HTTP_200_OK,
            )

        except ParticipentCycle.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Allocation not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )