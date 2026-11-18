from rest_framework import serializers
from .models import Constellation, Star, Planet, ObservationLog


class ConstellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Constellation
        fields = "__all__"


class StarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Star
        fields = "__all__"


class PlanetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planet
        fields = "__all__"


class ObservationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationLog
        fields = "__all__"