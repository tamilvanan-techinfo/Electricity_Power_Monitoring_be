import random

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ParticipentCycle


class UpdateReadingAPIView(APIView):

    def post(self, request):

        cycle_id = request.data.get("cycle_id")
        voltage = request.data.get("voltage")
        amperage = request.data.get("amperage")
        power = request.data.get("power")

        try:
            allocation = ParticipentCycle.objects.get(pk=cycle_id)

            allocation.voltage = voltage
            allocation.amperage = amperage
            allocation.power = power
            allocation.save()

            return Response(
                {
                    "status": "success",
                    "cycle": allocation.cycle.cycle_no,
                    "voltage": allocation.voltage,
                    "amperage": allocation.amperage,
                    "power": allocation.power,
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