from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from member.models import User, Profile
from reviews.models import Review
from library.models import UserLibrary
from interactions.models import Favorite, Like

from .serializers import ProfileSerializer
from api.interactions.serializers import FavoriteSerializer
from api.library.serializers import UserLibrarySerializer
from api.reviews.serializers import ReviewSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'username'
    
    def get_queryset(self):
        return Profile.objects.select_related('user').all()
    
    def get_object(self):
        """Get profile by username from URL"""
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.profile
    
    # PROFILE MANAGEMENT
    def retrieve(self, request, username=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def partial_update(self, request, username=None):
        profile = self.get_object()
        
        if request.user != profile.user:
            return Response(
                {'error': 'You can only edit your own profile'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(
        detail=True, 
        methods=['post'],
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser]
    )
    def upload_avatar(self, request, username=None):
        profile = self.get_object()
        
        if request.user != profile.user:
            return Response(
                {'error': 'You can only upload your own avatar'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old avatar
        if profile.avatar:
            profile.avatar.delete(save=False)
        
        # Save new avatar
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        serializer = self.get_serializer(profile)
        return Response({
            'message': 'Avatar uploaded successfully',
            'profile': serializer.data
        })
    
    # USER DATA    
    @action(detail=True, methods=['get'])
    def stats(self, request, username=None):
        user = self.get_object().user
        
        # Reviews stats
        reviews = Review.objects.filter(user=user)
        reviews_stats = {
            'total': reviews.count(),
            'comics': reviews.filter(comic__isnull=False).count(),
            'novels': reviews.filter(novel__isnull=False).count(),
            'average_rating': round(float(reviews.aggregate(avg=Avg('rating'))['avg'] or 0), 2),
            'likes_received': Like.objects.filter(review__user=user).count(),
        }
        
        # Library stats
        library = UserLibrary.objects.filter(user=user)
        library_stats = {
            'total': library.count(),
            'reading': library.filter(status='reading').count(),
            'completed': library.filter(status='completed').count(),
            'plan_to_read': library.filter(status='plan_to_read').count(),
            'dropped': library.filter(status='dropped').count(),
        }
        
        # Favorites stats
        favorites = Favorite.objects.filter(user=user)
        favorites_stats = {
            'total': favorites.count(),
            'comics': favorites.filter(comic__isnull=False).count(),
            'novels': favorites.filter(novel__isnull=False).count(),
        }
        
        return Response({
            'reviews': reviews_stats,
            'library': library_stats,
            'favorites': favorites_stats
        })
    
    @action(detail=True, methods=['get'])
    def favorites(self, request, username=None):
        user = self.get_object().user
        queryset = Favorite.objects.filter(user=user).select_related('comic', 'novel').order_by('rank')
        
        # Filter by type
        type_param = request.query_params.get('type')
        if type_param == 'comic':
            queryset = queryset.filter(comic__isnull=False)
        elif type_param == 'novel':
            queryset = queryset.filter(novel__isnull=False)
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FavoriteSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = FavoriteSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def library(self, request, username=None):
        user = self.get_object().user
        queryset = UserLibrary.objects.filter(user=user).select_related('comic', 'novel').order_by('-updated_at')
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserLibrarySerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = UserLibrarySerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, username=None):
        user = self.get_object().user
        queryset = Review.objects.filter(user=user).select_related('comic', 'novel').order_by('-created_at')
        
        # Search
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(comic__title__icontains=search) |
                Q(novel__title__icontains=search)
            )
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)