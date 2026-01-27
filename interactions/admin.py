from django.contrib import admin
from .models import Favorite, Like


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "get_target", "rank", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "comic__title", "novel__title")
    ordering = ("user", "rank")
    readonly_fields = ("created_at",)
    
    raw_id_fields = ("user", "comic", "novel")
    
    def get_target(self, obj):
        """Display target comic/novel"""
        if obj.comic:
            return f"Comic: {obj.comic.title}"
        elif obj.novel:
            return f"Novel: {obj.novel.title}"
        return "-"
    get_target.short_description = "Target"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'comic', 'novel')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "get_review_snippet", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "review__content")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    
    raw_id_fields = ("user", "review")
    
    def get_review_snippet(self, obj):
        content = obj.review.content
        return content[:50] + "..." if len(content) > 50 else content
    get_review_snippet.short_description = "Review"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'review', 'review__user')