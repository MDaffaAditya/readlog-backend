from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce, Cast

from contents.models import Genre, Comic, Novel
from .serializers import GenreSerializer, ComicSerializer, NovelSerializer
from .permissions import IsAdminOrReadOnly
from .filters import ComicFilter, NovelFilter
from rest_framework.views import APIView
from reviews.models import Review

class StatsView(APIView):
    def get(self, request):
        data = {
            'total_comics': Comic.objects.count(),
            'total_novels': Novel.objects.count(),
            'total_genres': Genre.objects.count(),
            'total_reviews': Review.objects.count()
        }
        return Response(data)

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None 

class BaseContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author']
    ordering_fields = ['title', 'release_year', 'average_rating', 'updated_at', 'popularity']
    ordering = ['-popularity', '-updated_at']

    def get_queryset(self):
        # Mengambil model secara dinamis berdasarkan viewset
        model = self.queryset.model
        return model.objects.prefetch_related('genres').annotate(
            reviews_count_internal=Count('review', distinct=True),
            popularity=ExpressionWrapper(
                Coalesce(Cast(F('average_rating'), FloatField()), 0.0) *
                (Coalesce(Cast(F('reviews_count_internal'), FloatField()), 0.0) + 1.0),
                output_field=FloatField()
            )
        )

class ComicViewSet(BaseContentViewSet):
    queryset = Comic.objects.all()
    serializer_class = ComicSerializer
    filterset_class = ComicFilter

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cover(self, request, pk=None):
        comic = self.get_object()
        if 'cover_image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if comic.cover_image:
            comic.cover_image.delete(save=False)
        
        comic.cover_image = request.FILES['cover_image']
        comic.save()
        return Response({'message': 'Cover uploaded', 'comic': self.get_serializer(comic).data})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def recommendations(self, request):
        user = request.user
        if not user.is_authenticated:
            recommended = Comic.objects.filter(average_rating__gte=8.0).order_by('-average_rating')[:10]
        else:
            # Ambil genre dari library user (asumsi model UserLibrary ada)
            user_genres = Genre.objects.filter(comic__userlibrary__user=user).distinct()
            if user_genres.exists():
                recommended = Comic.objects.filter(
                    genres__in=user_genres,
                    average_rating__gte=7.0
                ).exclude(userlibrary__user=user).distinct().order_by('-average_rating')[:10]
            else:
                recommended = Comic.objects.filter(average_rating__gte=8.0).order_by('-average_rating')[:10]
        
        return Response(self.get_serializer(recommended, many=True).data)

class NovelViewSet(BaseContentViewSet):
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    filterset_class = NovelFilter

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cover(self, request, pk=None):
        novel = self.get_object()
        if 'cover_image' not in request.FILES:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if novel.cover_image:
            novel.cover_image.delete(save=False)
        
        novel.cover_image = request.FILES['cover_image']
        novel.save()
        return Response({'message': 'Cover uploaded', 'novel': self.get_serializer(novel).data})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def recommendations(self, request):
        user = request.user
        if not user.is_authenticated:
            recommended = Novel.objects.filter(average_rating__gte=8.0).order_by('-average_rating')[:10]
        else:
            user_genres = Genre.objects.filter(novel__userlibrary__user=user).distinct()
            if user_genres.exists():
                recommended = Novel.objects.filter(
                    genres__in=user_genres,
                    average_rating__gte=7.0
                ).exclude(userlibrary__user=user).distinct().order_by('-average_rating')[:10]
            else:
                recommended = Novel.objects.filter(average_rating__gte=8.0).order_by('-average_rating')[:10]
        
        return Response(self.get_serializer(recommended, many=True).data)