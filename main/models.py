from django.contrib.auth.models import User
from django.db import models


class Constellation(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название созвездия"
    )
    latin_name = models.CharField(
        max_length=100, verbose_name="Латинское название"
    )

    def __str__(self):
        return self.name


class Star(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название звезды"
    )
    constellation = models.ForeignKey(
        Constellation,
        on_delete=models.CASCADE,
        related_name="stars",
        verbose_name="Созвездие",
    )
    spectral_class = models.CharField(
        max_length=10, verbose_name="Спектральный класс"
    )
    distance_light_years = models.FloatField(
        verbose_name="Расстояние (св. лет)"
    )
    is_visible_naked_eye = models.BooleanField(
        default=True, verbose_name="Видна невооруженным глазом"
    )

    def __str__(self):
        return f"Звезда {self.name}"


class Planet(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название планеты"
    )
    star = models.ForeignKey(
        Star,
        on_delete=models.CASCADE,
        related_name="planets",
        verbose_name="Родительская звезда",
    )
    is_habitable = models.BooleanField(
        default=False, verbose_name="В зоне обитаемости"
    )

    def __str__(self):
        return f"Планета {self.name} (звезда {self.star.name})"


class ObservationLog(models.Model):
    observer = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Наблюдатель"
    )
    star = models.ForeignKey(
        Star, on_delete=models.CASCADE, verbose_name="Звезда"
    )
    date_observed = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата наблюдения"
    )
    notes = models.TextField(verbose_name="Заметки/Впечатления")

    def __str__(self):
        return (
            f"{self.observer.username} наблюдал(а) {self.star.name} ({self.date_observed.strftime('%d.%m.%Y')})"
        )