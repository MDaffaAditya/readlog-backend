from django.urls import path, include
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("", include("api.contents.urls")),
    path("reviews/", include("api.reviews.urls")),
    path("library/", include("api.library.urls")),
    path("interactions/", include("api.interactions.urls")),
    path("profiles/", include("api.profiles.urls")),
]

# Enable swagger doc
if settings.DEBUG:
    urlpatterns += [
        path("schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
