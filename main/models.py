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

    @property
    def stars_count(self):
        """Количество звёзд в созвездии"""
        return self.stars.count()

    @property
    def visible_stars_count(self):
        """Количество звёзд,  невооружённым глазом"""
        return self.stars.filter(is_visible_naked_eye=True).count()

    @property
    def visible_stars_percentage(self):
        """Процент видимых невооружённым глазом звёзд"""
        total = self.stars_count

        if total == 0:
            return 0.0

        return round(self.visible_stars_count / total * 100, 2)


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

    @property
    def distance_parsecs(self):
        """Расстояние до звезды в парсеках."""
        if self.distance_light_years is None: return 0.0

        # 1 парсек = 3,26156 светового года.
        return round(self.distance_light_years / 3.26156, 4)

    @property
    def light_travel_time_years(self):
        """Примерное время, за которое свет достигнет Земли"""
        if self.distance_light_years is None:
            return 0.0

        return round(self.distance_light_years, 2)

    @property
    def planets_count(self):
        """Общее количество планет у звезды"""
        return self.planets.count()

    @property
    def habitable_planets_count(self):
        """Количество обитаемых планет у звезды"""
        return self.planets.filter(is_habitable=True).count()

    @property
    def habitable_planets_percentage(self):
        """Процент обитаемых планет среди всех планет звезды"""
        total = self.planets_count

        if total == 0:
            return 0.0

        return round(self.habitable_planets_count / total * 100, 2)


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

    @property
    def distance_light_years(self):
        """Расстояние планеты через расстояние до её звезды"""
        return self.star.distance_light_years

    @property
    def light_travel_time_years(self):
        """Примерное время распространения света до планеты"""
        return self.star.light_travel_time_years


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