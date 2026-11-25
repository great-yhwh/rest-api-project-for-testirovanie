from rest_framework.routers import DefaultRouter
from .views import AstronomerProfileViewSet

router = DefaultRouter()
router.register(r"profiles", AstronomerProfileViewSet, basename="profile")

urlpatterns = router.urls
