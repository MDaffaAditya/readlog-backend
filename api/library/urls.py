from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserLibraryViewSet

router = DefaultRouter()
router.register(r"", UserLibraryViewSet, basename="library")

urlpatterns = [
    path("", include(router.urls)),
]
