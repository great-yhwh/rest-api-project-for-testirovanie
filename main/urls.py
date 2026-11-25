from rest_framework.routers import DefaultRouter
from .views import (
    ConstellationViewSet,
    StarViewSet,
    PlanetViewSet,
    ObservationLogViewSet,
)

router = DefaultRouter()
router.register(
    r"constellations", ConstellationViewSet, basename="constellation"
)
router.register(r"stars", StarViewSet, basename="star")
router.register(r"planets", PlanetViewSet, basename="planet")
router.register(r"logs", ObservationLogViewSet, basename="log")

urlpatterns = router.urls
