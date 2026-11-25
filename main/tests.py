from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from main.models import Constellation, Star, Planet


class ConstellationTests(TestCase):
    def setUp(self):
        self.constellation = Constellation.objects.create(
            name="Орион", latin_name="Orion"
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


class StarTests(TestCase):
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
            is_habitable=False
        )
        Planet.objects.create(
            name="Планета 4", star=self.star,
            is_habitable=False
        )

        self.assertEqual(self.star.habitable_planets_percentage, 50.0)

    def test_habitable_planets_percentage_without_planets(self):
        self.assertEqual(self.star.habitable_planets_percentage, 0.0)


class PlanetTests(TestCase):
    def setUp(self):
        constellation = Constellation.objects.create(name="Орион", latin_name="Orion")

        self.star = Star.objects.create(
            name="Звезда 1", constellation=constellation,
            spectral_class="ВОТ",  distance_light_years=250.0
        )

        self.planet = Planet.objects.create(
            name="Планета 1", star=self.star, is_habitable=True
        )

    def test_distance_light_years(self):
        self.assertEqual(self.planet.distance_light_years,250.0)

    def test_light_travel_time_years(self):
        self.assertEqual(self.planet.light_travel_time_years,250.0)


class ConstellationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.constellation = Constellation.objects.create(
            name="Орион", latin_name="Orion",
        )

    def test_list_constellations(self):
        response = self.client.get(reverse("constellation-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        data = response.data[0]
        self.assertEqual(data["id"], self.constellation.id)
        self.assertEqual(data["name"], "Орион")
        self.assertEqual(data["latin_name"], "Orion")

    def test_create_constellation(self):
        data = {"name": "Андромеда","latin_name": "Andromeda"}

        response = self.client.post(reverse("constellation-list"),data,format="json",
        )

        self.assertEqual(response.status_code, 201)

        constellation = Constellation.objects.get(pk=response.data["id"])

        self.assertEqual(constellation.name, "Андромеда")
        self.assertEqual(constellation.latin_name, "Andromeda")

    def test_retrieve_constellation(self):
        response = self.client.get(
            reverse(
                "constellation-detail",
                kwargs={"pk": self.constellation.pk},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Орион")

    def test_update_constellation(self):
        data = {
            "name": "Орион",
            "latin_name": "Orion Updated",
        }

        response = self.client.put(
            reverse(
                "constellation-detail",
                kwargs={"pk": self.constellation.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.constellation.refresh_from_db()

        self.assertEqual(
            self.constellation.latin_name,
            "Orion Updated",
        )

    def test_partial_update_constellation(self):
        data = {
            "name": "Орион Updated",
        }

        response = self.client.patch(
            reverse(
                "constellation-detail",
                kwargs={"pk": self.constellation.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.constellation.refresh_from_db()

        self.assertEqual(self.constellation.name, "Орион Updated")
        self.assertEqual(self.constellation.latin_name, "Orion")

    def test_delete_constellation(self):
        response = self.client.delete(
            reverse(
                "constellation-detail",
                kwargs={"pk": self.constellation.pk},
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Constellation.objects.filter(
                pk=self.constellation.pk,
            ).exists()
        )


class StarApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.constellation = Constellation.objects.create(
            name="Орион", latin_name="Orion"
        )

        self.star = Star.objects.create(
            name="Звезда 1",
            constellation=self.constellation,
            spectral_class="ВОТ",
            distance_light_years=548.0,
        )

    def test_list_stars(self):
        response = self.client.get(reverse("star-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        data = response.data[0]

        self.assertEqual(data["id"], self.star.id)
        self.assertEqual(data["name"], "Звезда 1")
        self.assertEqual(data["constellation"], self.constellation.id,)

    def test_create_star(self):
        data = {
            "name": "Звезда 2",
            "constellation": self.constellation.id,
            "spectral_class": "НЕ ВОТ",
            "distance_light_years": 860.0,
            "is_visible_naked_eye": True,
        }

        response = self.client.post(reverse("star-list"), data,format="json",)
        self.assertEqual(response.status_code, 201)
        star = Star.objects.get(pk=response.data["id"])
        self.assertEqual(star.name, "Звезда 2")
        self.assertEqual(star.constellation, self.constellation)
        self.assertEqual(star.spectral_class, "НЕ ВОТ")
        self.assertEqual(star.distance_light_years, 860.0)
        self.assertTrue(star.is_visible_naked_eye)

    def test_retrieve_star(self):
        response = self.client.get(reverse("star-detail",kwargs={"pk": self.star.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Звезда 1")

    def test_update_star(self):
        data = {
            "name": "Звезда не 1",
            "constellation": self.constellation.id,
            "spectral_class": "ФИГНЯ ВОТ",
            "distance_light_years": 600.0,
            "is_visible_naked_eye": False,
        }

        response = self.client.put(
            reverse("star-detail",
                kwargs={"pk": self.star.pk},
            ),
            data,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.star.refresh_from_db()
        self.assertEqual(self.star.name, "Звезда не 1")
        self.assertEqual(self.star.spectral_class, "ФИГНЯ ВОТ")
        self.assertEqual(self.star.distance_light_years, 600.0)
        self.assertFalse(self.star.is_visible_naked_eye)

    def test_partial_update_star(self):
        data = {
            "distance_light_years": 700.0,
        }

        response = self.client.patch(
            reverse(
                "star-detail",
                kwargs={"pk": self.star.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.star.refresh_from_db()

        self.assertEqual(self.star.distance_light_years, 700.0)
        self.assertEqual(self.star.name, "Звезда 1")

    def test_delete_star(self):
        response = self.client.delete(
            reverse(
                "star-detail",
                kwargs={"pk": self.star.pk},
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Star.objects.filter(pk=self.star.pk).exists()
        )


class PlanetApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        constellation = Constellation.objects.create(
            name="Орион",
            latin_name="Orion",
        )

        self.star = Star.objects.create(
            name="Звезда 1",
            constellation=constellation,
            spectral_class="ВОТ",
            distance_light_years=548.0,
        )

        self.planet = Planet.objects.create(
            name="Планета 1",
            star=self.star,
            is_habitable=True,
        )

    def test_list_planets(self):
        response = self.client.get(
            reverse("planet-list"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        data = response.data[0]

        self.assertEqual(data["id"], self.planet.id)
        self.assertEqual(data["name"], "Планета 1")
        self.assertEqual(data["star"], self.star.id)
        self.assertTrue(data["is_habitable"])

    def test_create_planet(self):
        data = {
            "name": "Планета 2",
            "star": self.star.id,
            "is_habitable": False,
        }

        response = self.client.post(
            reverse("planet-list"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        planet = Planet.objects.get(pk=response.data["id"])

        self.assertEqual(planet.name, "Планета 2")
        self.assertEqual(planet.star, self.star)
        self.assertFalse(planet.is_habitable)

    def test_retrieve_planet(self):
        response = self.client.get(
            reverse(
                "planet-detail",
                kwargs={"pk": self.planet.pk},
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Планета 1")

    def test_update_planet(self):
        data = {
            "name": "Планета ВАУ",
            "star": self.star.id,
            "is_habitable": False,
        }

        response = self.client.put(
            reverse(
                "planet-detail",
                kwargs={"pk": self.planet.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.planet.refresh_from_db()

        self.assertEqual(self.planet.name, "Планета ВАУ")
        self.assertFalse(self.planet.is_habitable)

    def test_partial_update_planet(self):
        data = {
            "is_habitable": False,
        }

        response = self.client.patch(
            reverse(
                "planet-detail",
                kwargs={"pk": self.planet.pk},
            ),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.planet.refresh_from_db()

        self.assertFalse(self.planet.is_habitable)
        self.assertEqual(self.planet.name, "Планета 1")

    def test_delete_planet(self):
        response = self.client.delete(
            reverse(
                "planet-detail",
                kwargs={"pk": self.planet.pk},
            ),
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Planet.objects.filter(pk=self.planet.pk).exists()
        )


class ObservationLogApiTests(TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.user = None

    def setUp(self):
        self.client = APIClient()

        self.observer = self.client.post(
            reverse("profile-list"),
            {
                "user": self.user.id,
            },
            format="json",
        )