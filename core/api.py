from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import stream_data_for_duration


class StreamAPIView(APIView):
    def post(self, request):
        # Accept JSON body with optional duration and interval
        payload = request.data.get('payload', {'message': 'stream'})
        duration = request.data.get('duration', 5)
        interval = request.data.get('interval', 0.5)
        # Enqueue the streaming task
        stream_data_for_duration.delay(payload, duration, interval)
        return Response({'status': 'queued', 'duration': duration, 'interval': interval}, status=status.HTTP_202_ACCEPTED)


class PingAPIView(APIView):
    def get(self, request):
        return Response(
            {'status': 'ok', 'message': 'Django REST Framework is configured successfully'},
            status=status.HTTP_200_OK,
        )
