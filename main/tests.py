from django.test import TestCase

from main.models import Constellation, Star, Planet


class ConstellationCalculationTests(TestCase):
    def setUp(self):
        self.constellation = Constellation.objects.create(
            name="Орион",
            latin_name="Orion"
        )

    def test_stars_count(self):
        Star.objects.create(
            name="Звезда 1", constellation=self.constellation,
            spectral_class="ВОТ", distance_light_years=548.0
        )
        Star.objects.create(
            name="Звезда 3", constellation=self.constellation,
            spectral_class="ОХ", distance_light_years=860.0
        )

        self.assertEqual(self.constellation.stars_count, 2)

    def test_visible_stars_count(self):
        Star.objects.create(
            name="Звезда", constellation=self.constellation,
            spectral_class="ВОТ", distance_light_years=548.0,
            is_visible_naked_eye=True
        )
        Star.objects.create(
            name="Точность", constellation=self.constellation,
            spectral_class="0", distance_light_years=2000.0,
            is_visible_naked_eye=False
        )

        self.assertEqual(self.constellation.visible_stars_count, 1)

    def test_visible_stars_percentage(self):
        Star.objects.create(
            name="Звезда 1", constellation=self.constellation,
            spectral_class="ВОТ", distance_light_years=548.0,
            is_visible_naked_eye=True
        )
        Star.objects.create(
            name="Звезда 3", constellation=self.constellation,
            spectral_class="ОХ", distance_light_years=860.0,
            is_visible_naked_eye=True
        )
        Star.objects.create(
            name="Невидимая звезда", constellation=self.constellation,
            spectral_class="Не видно", distance_light_years=10000.0,
            is_visible_naked_eye=False
        )

        self.assertEqual(self.constellation.visible_stars_percentage, 66.67)

    def test_visible_stars_percentage_for_empty_constellation(self):
        self.assertEqual(self.constellation.visible_stars_percentage, 0.0)


class StarCalculationTests(TestCase):
    def setUp(self):
        self.constellation = Constellation.objects.create(name="Орион",latin_name="Orion")

        self.star = Star.objects.create(
            name="Звезда 1", constellation=self.constellation,
            spectral_class="ВОТ", distance_light_years=100.0
        )

    def test_distance_parsecs(self):
        expected = round(100.0 / 3.26156, 4)
        self.assertEqual(self.star.distance_parsecs, expected)

    def test_light_travel_time_years(self):
        self.assertEqual(self.star.light_travel_time_years, 100.0)

    def test_planets_count(self):
        Planet.objects.create(
            name="Планета 1", star=self.star,
            is_habitable=True
        )
        Planet.objects.create(
            name="Планета 2", star=self.star,
            is_habitable=False
        )

        self.assertEqual(self.star.planets_count, 2)

    def test_habitable_planets_count(self):
        Planet.objects.create(
            name="Планета 1", star=self.star,
            is_habitable=True
        )
        Planet.objects.create(
            name="Планета 2", star=self.star,
            is_habitable=False
        )

        self.assertEqual(self.star.habitable_planets_count, 1)

    def test_habitable_planets_percentage(self):
        Planet.objects.create(
            name="Планета 1", star=self.star,
            is_habitable=True
        )
        Planet.objects.create(
            name="Планета 2", star=self.star,
            is_habitable=True
        )
        Planet.objects.create(
            name="Планета 3",
            star=self.star,
            is_habitable=False,
        )
        Planet.objects.create(
            name="Планета 4", star=self.star,
            is_habitable=False
        )

        self.assertEqual(self.star.habitable_planets_percentage, 50.0)

    def test_habitable_planets_percentage_without_planets(self):
        self.assertEqual(self.star.habitable_planets_percentage, 0.0)


class PlanetCalculationTests(TestCase):
    def setUp(self):
        constellation = Constellation.objects.create(name="Орион", latin_name="Orion",)

        self.star = Star.objects.create(
            name="Звезда 1",
            constellation=constellation,
            spectral_class="M1",
            distance_light_years=250.0,
        )

        self.planet = Planet.objects.create(
            name="Планета 1",
            star=self.star,
            is_habitable=True,
        )

    def test_distance_light_years(self):
        self.assertEqual(
            self.planet.distance_light_years,
            250.0,
        )

    def test_light_travel_time_years(self):
        self.assertEqual(
            self.planet.light_travel_time_years,
            250.0,
        )
