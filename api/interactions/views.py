from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction

from interactions.models import Favorite, Like
from reviews.models import Review
from .serializers import FavoriteSerializer, FavoriteReorderSerializer, LikeSerializer, LikeToggleSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['comic__title', 'novel__title', 'comic__author', 'novel__author']
    ordering_fields = ['rank', 'created_at']
    ordering = ['rank']

    def get_queryset(self):
        username = self.request.query_params.get('username')
        if username:
            from member.models import User
            from django.shortcuts import get_object_or_404
            user = get_object_or_404(User, username=username)
            queryset = Favorite.objects.filter(user=user)
        else:
            if not self.request.user.is_authenticated:
                return Favorite.objects.none()
            queryset = Favorite.objects.filter(user=self.request.user)
        type_filter = self.request.query_params.get('type')
        if type_filter == 'comic':
            queryset = queryset.filter(comic__isnull=False)
        elif type_filter == 'novel':
            queryset = queryset.filter(novel__isnull=False)
        return queryset.select_related('comic', 'novel').order_by('rank')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        serializer = FavoriteReorderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorites_data = serializer.validated_data['favorites']
        with transaction.atomic():
            for item in favorites_data:
                Favorite.objects.filter(id=item['id'], user=request.user).update(rank=item['rank'])
        return Response({'message': 'Favorites reordered successfully', 'count': len(favorites_data)})


class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['review']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user).select_related('review', 'review__user')

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        serializer = LikeToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review_id = serializer.validated_data['review']
        review = Review.objects.get(id=review_id)
        like, created = Like.toggle(user=request.user, review=review)
        likes_count = review.likes.count()
        return Response({
            'liked': created,
            'likes_count': likes_count,
            'message': 'Review liked' if created else 'Review unliked'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
