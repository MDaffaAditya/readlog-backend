from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "get_target", "rating", "get_content_snippet", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("content", "user__username", "comic__title", "novel__title")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    
    raw_id_fields = ("user", "comic", "novel")
    
    fieldsets = (
        ("Review Info", {
            "fields": ("user", "content", "rating")
        }),
        ("Target", {
            "fields": ("comic", "novel"),
            "description": "Select either Comic OR Novel, not both"
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    
    def get_target(self, obj):
        if obj.comic:
            return f"Comic: {obj.comic.title}"
        elif obj.novel:
            return f"Novel: {obj.novel.title}"
        return "-"
    get_target.short_description = "Target"
    
    def get_content_snippet(self, obj):
        content = obj.content
        return content[:50] + "..." if len(content) > 50 else content
    get_content_snippet.short_description = "Content"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'comic', 'novel')