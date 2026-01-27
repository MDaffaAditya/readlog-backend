from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg, F, Case, When, FloatField

from library.models import UserLibrary
from .serializers import UserLibrarySerializer
from .filters import UserLibraryFilter

class UserLibraryViewSet(viewsets.ModelViewSet):
    serializer_class = UserLibrarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserLibraryFilter
    
    search_fields = ["comic__title", "novel__title", "comic__author", "novel__author"]
    ordering_fields = ["updated_at", "created_at", "progress", "started_at", "completed_at"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        username = self.request.query_params.get('username')
        
        if username:
            from member.models import User
            user = get_object_or_404(User, username=username)
            queryset = UserLibrary.objects.filter(user=user)
        else:
            if not self.request.user.is_authenticated:
                return UserLibrary.objects.none()
            queryset = UserLibrary.objects.filter(user=self.request.user)

        return queryset.select_related("user", "comic", "novel").prefetch_related(
            "comic__genres", "novel__genres"
        )

    def get_permissions(self):
        """Pastikan hanya user yang login yang bisa mutasi data"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Auto-assign user saat create"""
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Validasi duplikasi"""
        comic_id = request.data.get("comic")
        novel_id = request.data.get("novel")

        if comic_id and UserLibrary.objects.filter(user=request.user, comic_id=comic_id).exists():
            return Response(
                {"detail": "This comic is already in your library."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if novel_id and UserLibrary.objects.filter(user=request.user, novel_id=novel_id).exists():
            return Response(
                {"detail": "This novel is already in your library."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Ownership check"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "You can only edit your own library."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Ownership check for PATCH"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "You can only edit your own library."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Ownership check"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "You can only delete your own library."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistik library user"""
        username = request.query_params.get('username')
        if username:
            from member.models import User
            user = get_object_or_404(User, username=username)
        else:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user = request.user
            
        queryset = UserLibrary.objects.filter(user=user)
        
        # Stats by status
        by_status = {
            key: queryset.filter(status=key).count() 
            for key, _ in UserLibrary.STATUS_CHOICES
        }
        
        # Stats by type
        by_type = {
            "comic": queryset.filter(comic__isnull=False).count(),
            "novel": queryset.filter(novel__isnull=False).count(),
        }
        
        # Average completion (lebih efisien dengan aggregation)
        avg_completion = queryset.aggregate(
            avg=Avg(
                Case(
                    When(comic__isnull=False, then=F('progress') * 100.0 / F('comic__total_chapters')),
                    When(novel__isnull=False, then=F('progress') * 100.0 / F('novel__total_chapters')),
                    default=0.0,
                    output_field=FloatField()
                )
            )
        )['avg'] or 0.0
        
        return Response({
            "total": queryset.count(), 
            "by_status": by_status, 
            "by_type": by_type, 
            "avg_completion": round(avg_completion, 2)
        })