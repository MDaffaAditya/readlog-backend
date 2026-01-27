import django_filters
from django.db.models import Q
from contents.models import Comic, Novel


class ComicFilter(django_filters.FilterSet):
    genre_name = django_filters.CharFilter(field_name='genres__name', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    release_year = django_filters.NumberFilter(field_name='release_year')

    class Meta:
        model = Comic
        fields = ['comic_type', 'status', 'release_year']


class NovelFilter(django_filters.FilterSet):
    genre_name = django_filters.CharFilter(field_name='genres__name', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    release_year = django_filters.NumberFilter(field_name='release_year')

    class Meta:
        model = Novel
        fields = ['novel_type', 'status', 'release_year']