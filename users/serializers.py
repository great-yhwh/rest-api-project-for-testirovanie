from rest_framework import serializers
from .models import AstronomerProfile


class AstronomerProfileSerializer(serializers.ModelSerializer):
    observations_count = serializers.IntegerField(read_only=True)
    unique_observed_stars_count = serializers.IntegerField(read_only=True)
    activity_index = serializers.IntegerField(read_only=True)

    class Meta:
        model = AstronomerProfile
        fields = [
            "id",
            "user",
            "bio",
            "telescope_model",
            "observations_count",
            "unique_observed_stars_count",
            "activity_index",
        ]
