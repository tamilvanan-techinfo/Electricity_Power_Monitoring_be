from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
from core.models import  *
from rest_framework.permissions import AllowAny


class WindoePositionalAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self,request):
        
        try:
            data = ScreenPosition.objects.first()
            serializers = ScreenPositionSerializer(data,many=False)
            return Response(serializers.data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(str(e),status=status.HTTP_404_NOT_FOUND)


class ParticipentCycleAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self,request):
        try:
            response = []
            data = ParticipentCycle.objects.all()
            for d in data:
                response.append({
                    'id':d.id,
                    'name':d.participent.name,
                    'cycle':d.cycle.cycle_no,
                   
                })
                
            return Response(response,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(str(e),status=status.HTTP_404_NOT_FOUND)


class SelectedCyclesAPI(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def get(self,request):
        try:
            data = ActiveParticipent.objects.get(id=1)
            
            # Convert HH:MM:SS to total minutes
            duration_minutes = (
                data.time_duration.hour * 60
                + data.time_duration.minute
                + data.time_duration.second // 60
            )
    
            response = {
                "duration": duration_minutes,
                "cycles": list(data.cycle.values_list("cycle_no", flat=True))
            }
    
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(str(e), status=status.HTTP_404_NOT_FOUND)

        