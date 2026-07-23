from rest_framework import serializers
from .models import Screen


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = "__all__"