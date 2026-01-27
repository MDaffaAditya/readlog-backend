from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, ComicViewSet, NovelViewSet, StatsView

router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"comics", ComicViewSet, basename="comic")
router.register(r"novels", NovelViewSet, basename="novel")

urlpatterns = [
    path('stats/', StatsView.as_view(), name='stats'),
    path("", include(router.urls)),
]
