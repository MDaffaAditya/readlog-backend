from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Review
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related("user", "comic", "novel")
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["comic", "novel", "rating", "user", "user__username"]
    search_fields = ["content", "user__username", "comic__title", "novel__title"]
    ordering_fields = ["created_at", "rating"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You can only edit your own review."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You can only delete your own review."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        review = serializer.save()
        if review.comic:
            review.comic.update_average_rating()
        if review.novel:
            review.novel.update_average_rating()

    def perform_destroy(self, instance):
        comic = instance.comic
        novel = instance.novel
        instance.delete()
        if comic:
            comic.update_average_rating()
        if novel:
            novel.update_average_rating()
