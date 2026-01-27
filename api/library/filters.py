from django_filters import rest_framework as django_filters
from django.db.models import F, ExpressionWrapper, FloatField, Case, When, Q
from library.models import UserLibrary

class UserLibraryFilter(django_filters.FilterSet):
    # 1. Filter Status
    status = django_filters.ChoiceFilter(choices=UserLibrary.STATUS_CHOICES)
    
    # 2. Filter Tipe - PERBAIKAN: gunakan method untuk lebih jelas
    media_type = django_filters.CharFilter(method='filter_by_media_type')

    # 3. Filter Genre
    genre = django_filters.CharFilter(method='filter_by_genre')

    # 4. Filter Completion
    completion_gte = django_filters.NumberFilter(method='filter_completion_gte')
    completion_lte = django_filters.NumberFilter(method='filter_completion_lte')

    # 5. Filter Rentang Waktu
    started_after = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='gte')
    started_before = django_filters.DateTimeFilter(field_name='started_at', lookup_expr='lte')
    completed_after = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='gte')
    completed_before = django_filters.DateTimeFilter(field_name='completed_at', lookup_expr='lte')
    
    class Meta:
        model = UserLibrary
        fields = ['status']

    def filter_by_media_type(self, queryset, name, value):
        """Filter by comic/novel/all"""
        if value == 'comic':
            return queryset.filter(comic__isnull=False)
        elif value == 'novel':
            return queryset.filter(novel__isnull=False)
        # 'all' atau value lain: return semua
        return queryset

    def filter_by_genre(self, queryset, name, value):
        """Mencari genre berdasarkan nama"""
        if not value:
            return queryset
        return queryset.filter(
            Q(comic__genres__name__icontains=value) | 
            Q(novel__genres__name__icontains=value)
        ).distinct()

    def filter_completion_gte(self, queryset, name, value):
        return self.annotate_completion(queryset).filter(calc_perc__gte=value)

    def filter_completion_lte(self, queryset, name, value):
        return self.annotate_completion(queryset).filter(calc_perc__lte=value)

    def annotate_completion(self, queryset):
        """Helper kalkulasi persentase dinamis"""
        return queryset.annotate(
            calc_perc=ExpressionWrapper(
                (F('progress') * 100.0) / Case(
                    When(comic__isnull=False, then=F('comic__total_chapters')),
                    When(novel__isnull=False, then=F('novel__total_chapters')),
                    default=1.0
                ), 
                output_field=FloatField()
            )
        )