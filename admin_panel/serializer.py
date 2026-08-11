from rest_framework import serializers
from core.models import Cycle, Participent, ParticipentCycle, AppTheme


class CycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cycle
        fields = "__all__"


class ParticipentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participent
        fields = "__all__"


class ParticipentCycleSerializer(serializers.ModelSerializer):
    participent_name = serializers.CharField(source="participent.name", read_only=True)
    cycle_no = serializers.CharField(source="cycle.cycle_no", read_only=True)
    controller_no = serializers.CharField(source="cycle.controller_no", read_only=True)

    class Meta:
        model = ParticipentCycle
        fields = "__all__"


from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password,
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid username or password."
            )

        attrs["user"] = user

        return attrs

class AppThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppTheme
        fields = "__all__"