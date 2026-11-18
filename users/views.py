from rest_framework import viewsets
from .models import AstronomerProfile
from .serializers import AstronomerProfileSerializer


class AstronomerProfileViewSet(viewsets.ModelViewSet):
    queryset = AstronomerProfile.objects.all()
    serializer_class = AstronomerProfileSerializer