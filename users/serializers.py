from rest_framework import serializers
from .models import AstronomerProfile


class AstronomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomerProfile
        fields = "__all__"