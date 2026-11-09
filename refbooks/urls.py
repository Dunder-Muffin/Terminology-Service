from rest_framework.routers import DefaultRouter

from .views import RefBookViewSet

router = DefaultRouter()
router.register("refbooks", RefBookViewSet)

urlpatterns = router.urls
