from rest_framework import viewsets
from .models import Constellation, Star, Planet, ObservationLog
from .serializers import (
    ConstellationSerializer,
    StarSerializer,
    PlanetSerializer,
    ObservationLogSerializer,
)


class ConstellationViewSet(viewsets.ModelViewSet):
    queryset = Constellation.objects.all()
    serializer_class = ConstellationSerializer


class StarViewSet(viewsets.ModelViewSet):
    queryset = Star.objects.all()
    serializer_class = StarSerializer


class PlanetViewSet(viewsets.ModelViewSet):
    queryset = Planet.objects.all()
    serializer_class = PlanetSerializer


class ObservationLogViewSet(viewsets.ModelViewSet):
    queryset = ObservationLog.objects.all()
    serializer_class = ObservationLogSerializer
