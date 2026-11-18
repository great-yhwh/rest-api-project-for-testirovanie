from django.contrib.auth.models import User
from django.db import models


class AstronomerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    telescope_model = models.CharField(
        max_length=100, blank=True, verbose_name="Модель телескопа"
    )

    def __str__(self):
        return f"Астроном {self.user.username}"