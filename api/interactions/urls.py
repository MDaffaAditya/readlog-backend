from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import FavoriteViewSet, LikeViewSet

router = DefaultRouter()
router.register("favorites", FavoriteViewSet, basename="favorite")
router.register("likes", LikeViewSet, basename="like")

urlpatterns = [
    path("", include(router.urls)),
]
