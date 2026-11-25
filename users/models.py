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

    @property
    def observations_count(self):
        """Количество наблюдений пользователя"""
        return self.user.observation_logs.count()

    @property
    def unique_observed_stars_count(self):
        """Количество уникальных наблюдённых звёзд"""
        return (
            self.user.observation_logs
            .values("star_id")
            .distinct()
            .count()
        )

    @property
    def activity_index(self):
        """
        Индекс активности:
        2 балла за каждое наблюдение и 1 балл за уникальную звезду.
        """
        return self.observations_count * 2 + self.unique_observed_stars_count