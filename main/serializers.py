from rest_framework import serializers
from .models import Constellation, Star, Planet, ObservationLog


class ConstellationSerializer(serializers.ModelSerializer):
    stars_count = serializers.IntegerField(read_only=True)
    visible_stars_count = serializers.IntegerField(read_only=True)
    visible_stars_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Constellation
        fields = [
            "id",
            "name",
            "latin_name",
            "stars_count",
            "visible_stars_count",
            "visible_stars_percentage",
        ]


class StarSerializer(serializers.ModelSerializer):
    distance_parsecs = serializers.FloatField(read_only=True)
    light_travel_time_years = serializers.FloatField(read_only=True)
    planets_count = serializers.IntegerField(read_only=True)
    habitable_planets_count = serializers.IntegerField(read_only=True)
    habitable_planets_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Star
        fields = [
            "id",
            "name",
            "constellation",
            "spectral_class",
            "distance_light_years",
            "distance_parsecs",
            "light_travel_time_years",
            "is_visible_naked_eye",
            "planets_count",
            "habitable_planets_count",
            "habitable_planets_percentage",
        ]


class PlanetSerializer(serializers.ModelSerializer):
    distance_light_years = serializers.FloatField(read_only=True)
    light_travel_time_years = serializers.FloatField(read_only=True)

    class Meta:
        model = Planet
        fields = [
            "id",
            "name",
            "star",
            "is_habitable",
            "distance_light_years",
            "light_travel_time_years",
        ]


class ObservationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationLog
        fields = [
            "id",
            "observer",
            "star",
            "date_observed",
            "notes",
        ]