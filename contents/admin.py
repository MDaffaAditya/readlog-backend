from django.contrib import admin
from .models import Genre, Comic, Novel


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_comics_count", "get_novels_count")
    search_fields = ("name",)
    ordering = ("name",)
    
    def get_comics_count(self, obj):
        return obj.comic_set.count()
    get_comics_count.short_description = "Comics"
    
    def get_novels_count(self, obj):
        return obj.novel_set.count()
    get_novels_count.short_description = "Novels"


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = (
        "id", 
        "title", 
        "author", 
        "comic_type", 
        "status", 
        "average_rating",
        "total_chapters",
        "release_year"
    )
    list_filter = ("comic_type", "status", "release_year", "genres")
    search_fields = ("title", "author")
    filter_horizontal = ("genres",) 
    ordering = ("-updated_at",)
    readonly_fields = ("average_rating", "updated_at")
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "author", "comic_type", "status")
        }),
        ("Details", {
            "fields": ("description", "genres", "release_year", "cover_image")
        }),
        ("Stats", {
            "fields": ("total_chapters", "total_volumes", "average_rating")
        }),
        ("Timestamps", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('genres')


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    """Admin interface untuk Novel"""
    list_display = (
        "id", 
        "title", 
        "author", 
        "novel_type", 
        "status", 
        "average_rating",
        "total_chapters",
        "release_year"
    )
    list_filter = ("novel_type", "status", "release_year", "genres")
    search_fields = ("title", "author")
    filter_horizontal = ("genres",)
    ordering = ("-updated_at",)
    readonly_fields = ("average_rating", "updated_at")
    
    fieldsets = (
        ("Basic Info", {
            "fields": ("title", "author", "novel_type", "status")
        }),
        ("Details", {
            "fields": ("description", "genres", "release_year", "cover_image")
        }),
        ("Stats", {
            "fields": ("total_chapters", "total_volumes", "average_rating")
        }),
        ("Timestamps", {
            "fields": ("updated_at",),
            "classes": ("collapse",)
        }),
    )

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('genres')