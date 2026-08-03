from rest_framework import serializers
from core.models import Cycle, Participent, ParticipentCycle


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

    participent = serializers.PrimaryKeyRelatedField(queryset=Participent.objects.all())
    cycle = serializers.PrimaryKeyRelatedField(queryset=Cycle.objects.all())
    participent_profile = serializers.SerializerMethodField()

    def get_participent_profile(self, obj):
        request = self.context.get("request")
        if obj.participent.profile and request:
            return request.build_absolute_uri(obj.participent.profile.url)
        return None

    class Meta:
        model = ParticipentCycle
        fields = [
        "id",
        "participent",
        "participent_name",
        "participent_profile",
        "cycle",
        "cycle_no",
        "controller_no",
        "power",
        "voltage",
        "amperage",
        "total_power",
        "total_voltage",
        "total_amperage",
        "updated_at",
    ]


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