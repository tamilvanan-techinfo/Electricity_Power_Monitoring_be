from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import Cycle, Participent, ParticipentCycle
from screen_controller.models import Screen
from screen_controller.serializer import *
from .serializer import (
    CycleSerializer,
    ParticipentSerializer,
    ParticipentCycleSerializer,
)



from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken

from .serializer import LoginSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import F

class LoginAPIView(APIView):
    # Allow anyone to call this endpoint (overrides DEFAULT_PERMISSION_CLASSES)
    permission_classes = [AllowAny]
    authentication_classes = []  # optional, avoids JWT/session checks on login

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "status": True,
                    "message": "Login successful.",
                    "data": {
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "message": "Login failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
class CycleAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self, request, pk=None):

        if pk:
            try:
                cycle = Cycle.objects.get(pk=pk)
            except Cycle.DoesNotExist:
                return Response(
                    {
                        "status": False,
                        "message": "Cycle not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = CycleSerializer(cycle)
            return Response(
                {
                    "status": True,
                    "message": "Cycle fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        cycles = Cycle.objects.all().order_by("id")
        serializer = CycleSerializer(cycles, many=True)

        return Response(
            {
                "status": True,
                "message": "Cycles fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = CycleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Cycle created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to create cycle.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):

        try:
            cycle = Cycle.objects.get(pk=pk)
        except Cycle.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Cycle not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CycleSerializer(
            cycle,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Cycle updated successfully.",
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "status": False,
                "message": "Unable to update cycle.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        try:
            cycle = Cycle.objects.get(pk=pk)
        except Cycle.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Cycle not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        cycle.delete()

        return Response(
            {
                "status": True,
                "message": "Cycle deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
    
class LogoutAPIView(APIView):
    # You can choose either:
    # - AllowAny if you only depend on the refresh token in body
    # - IsAuthenticated if you want the user to still be logged in to log out
    permission_classes = [AllowAny]
    authentication_classes = []  # optional, similar reason as LoginAPIView

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "status": True,
                    "message": "Logout successful.",
                }
            )

        except Exception:
            return Response(
                {
                    "status": False,
                    "message": "Invalid refresh token.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ParticipentAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self, request, pk=None):

        if pk:
            try:
                participent = Participent.objects.get(pk=pk)
            except Participent.DoesNotExist:
                return Response(
                    {
                        "status": False,
                        "message": "Participant not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ParticipentSerializer(participent)

            return Response(
                {
                    "status": True,
                    "message": "Participant fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        participents = Participent.objects.all().order_by("id")
        serializer = ParticipentSerializer(participents, many=True)

        return Response(
            {
                "status": True,
                "message": "Participants fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = ParticipentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Participant created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to create participant.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):

        try:
            participent = Participent.objects.get(pk=pk)
        except Participent.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Participant not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ParticipentSerializer(
            participent,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Participant updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to update participant.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        try:
            participent = Participent.objects.get(pk=pk)
        except Participent.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Participant not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        participent.delete()

        return Response(
            {
                "status": True,
                "message": "Participant deleted successfully."
            },
            status=status.HTTP_200_OK,
        ) 

class ParticipentCycleAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self, request, pk=None):

        if pk:
            try:
                allocation = ParticipentCycle.objects.get(pk=pk)
            except ParticipentCycle.DoesNotExist:
                return Response(
                    {
                        "status": False,
                        "message": "Allocation not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ParticipentCycleSerializer(allocation, context={"request": request})


            return Response(
                {
                    "status": True,
                    "message": "Allocation fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        allocations = (
            ParticipentCycle.objects
            .select_related("participent", "cycle")
            .all()
            .order_by("id")
        )

        serializer = ParticipentCycleSerializer(allocations, many=True, context={"request": request})

        return Response(
            {
                "status": True,
                "message": "Allocations fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        cycle_id = request.data.get("cycle")

        if ParticipentCycle.objects.filter(cycle_id=cycle_id).exists():
            return Response(
                {
                    "status": False,
                    "message": "Cycle is already allocated."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ParticipentCycleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Cycle allocated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to allocate cycle.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):

        try:
            allocation = ParticipentCycle.objects.get(pk=pk)
        except ParticipentCycle.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Allocation not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        cycle_id = request.data.get("cycle")

        if cycle_id:
            exists = ParticipentCycle.objects.filter(
                cycle_id=cycle_id
            ).exclude(pk=pk)

            if exists.exists():
                return Response(
                    {
                        "status": False,
                        "message": "Cycle is already allocated."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Get current readings from request
        update_data = {}
        data = request.data

        if "participent" in request.data:
            allocation.participent_id = data['participent']
            allocation.save()

        if "cycle" in request.data:
            allocation.cycle_id = data['cycle']
            allocation.save()
        if "power" in request.data:
            allocation.total_power  += data['power']
            allocation.power = data['power']
            allocation.save()

        if "voltage" in request.data:
            allocation.total_voltage+=data['voltage']
            allocation.voltage = data['voltage']
            allocation.save()
            
       

        if "amperage" in request.data:
            allocation.total_amperage+=data['amperage']
            allocation.amperage = data['amperage']
            allocation.save()
        

        # # Update current readings and increment totals
        # ParticipentCycle.objects.filter(pk=pk).update(**update_data)

        # Reload updated object
        allocation.refresh_from_db()

        serializer = ParticipentCycleSerializer(allocation, context={"request": request})

        return Response(
                {
                    "status": True,
                    "message": "Allocation updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

       

    def delete(self, request, pk):

        try:
            allocation = ParticipentCycle.objects.get(pk=pk)
        except ParticipentCycle.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Allocation not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        allocation.delete()

        return Response(
            {
                "status": True,
                "message": "Allocation deleted successfully."
            },
            status=status.HTTP_200_OK,
        )

class ScreenAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 
    def get(self, request, pk=None):

        if pk:
            try:
                screen = Screen.objects.get(pk=pk)
            except Screen.DoesNotExist:
                return Response(
                    {
                        "status": False,
                        "message": "Screen not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ScreenSerializer(screen)

            return Response(
                {
                    "status": True,
                    "message": "Screen fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        screens = Screen.objects.all().order_by("id")
        serializer = ScreenSerializer(screens, many=True)

        return Response(
            {
                "status": True,
                "message": "Screens fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):

        serializer = ScreenSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Screen created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to create screen.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, pk):

        try:
            screen = Screen.objects.get(pk=pk)
        except Screen.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Screen not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ScreenSerializer(
            screen,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Screen updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "message": "Unable to update screen.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):

        try:
            screen = Screen.objects.get(pk=pk)
        except Screen.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Screen not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        screen.delete()

        return Response(
            {
                "status": True,
                "message": "Screen deleted successfully."
            },
            status=status.HTTP_200_OK,
        )
    


class Available_Cycle(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def get(self,request):
        try:
            allocated_cycles = ParticipentCycle.objects.values_list('cycle_id', flat=True)
            available_cycles = Cycle.objects.exclude(id__in=allocated_cycles)

            serializer = CycleSerializer(available_cycles, many=True)

            return Response(
                {
                    "status": True,
                    "message": "Available cycles fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Error fetching available cycles.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class AvailableParticipant(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def get(self,request):
        try:
            allocated_data = ParticipentCycle.objects.values_list('participent_id', flat=True)
            available_data = Participent.objects.exclude(id__in=allocated_data)

            participent = ParticipentSerializer(available_data,many=True)
            return Response(
                {
                    "status": True,
                    "message": "Available cycles fetched successfully.",
                    "data": participent.data,
                },
                status=status.HTTP_200_OK,
            )


        except Exception as e:
            return Response(
                {
                    "status":False,
                    "message":"Error fetching availabe cycles",
                    "error":str(e)
                }
            )
