from django.test import TestCase
from django.contrib.auth.models import User
from main.models import Constellation, Star, ObservationLog
from users.models import AstronomerProfile


class AstronomerProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="astronom", password="password")
        self.profile = AstronomerProfile.objects.create(
            user=self.user, bio="Наблюдаю звёзды, очень нравится",
            telescope_model="Telescope"
        )

        constellation = Constellation.objects.create(name="Орион", latin_name="Orion")
        self.star = Star.objects.create(
            name="Звезда 1", constellation=constellation,
            spectral_class="ВОТ", distance_light_years=548.0
        )

        self.another_star = Star.objects.create(
            name="Звезда 2", constellation=constellation,
            spectral_class="НЕ ВОТ", distance_light_years=860.0
        )

    def test_observations_count(self):
        ObservationLog.objects.create(
            observer=self.user, star=self.star, notes="Первое наблюдение"
        )
        ObservationLog.objects.create(
            observer=self.user, star=self.another_star, notes="Второе наблюдение"
        )
        self.assertEqual(self.profile.observations_count, 2)

    def test_unique_observed_stars_count(self):
        ObservationLog.objects.create(
            observer=self.user, star=self.star, notes="Первое наблюдение"
        )
        ObservationLog.objects.create(
            observer=self.user, star=self.star, notes="Второе наблюдение"
        )
        ObservationLog.objects.create(
            observer=self.user, star=self.another_star, notes="Другая звезда"
        )

        self.assertEqual(self.profile.unique_observed_stars_count, 2)

    def test_activity_index(self):
        ObservationLog.objects.create(
            observer=self.user, star=self.star, notes="Первое наблюдение"
        )
        ObservationLog.objects.create(
            observer=self.user, star=self.star, notes="Второе наблюдение"
        )

        self.assertEqual(self.profile.activity_index, 5)

    def test_activity_index_without_observations(self):
        self.assertEqual(self.profile.activity_index, 0)
