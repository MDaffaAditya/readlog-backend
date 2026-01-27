from django.contrib import admin
from .models import UserLibrary


@admin.register(UserLibrary)
class UserLibraryAdmin(admin.ModelAdmin):
    """
    Improved admin interface untuk User Library
    """
    list_display = (
        "id", 
        "user", 
        "get_target", 
        "status", 
        "progress",
        "get_completion",
        "started_at",
        "completed_at",
        "updated_at"
    )
    list_filter = ("status", "started_at", "completed_at", "updated_at")
    search_fields = ("user__username", "comic__title", "novel__title")
    ordering = ("-updated_at",)
    readonly_fields = ("started_at", "completed_at", "created_at", "updated_at", "get_completion")
    
    # Use raw_id_fields for better performance
    raw_id_fields = ("user", "comic", "novel")
    
    # Group fields logically
    fieldsets = (
        ("User & Target", {
            "fields": ("user", "comic", "novel")
        }),
        ("Reading Info", {
            "fields": ("status", "progress", "get_completion")
        }),
        ("Timestamps", {
            "fields": ("started_at", "completed_at", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_target(self, obj):
        """Display target comic/novel with type"""
        if obj.comic:
            return f"Comic: {obj.comic.title}"
        elif obj.novel:
            return f"Novel: {obj.novel.title}"
        return "-"
    get_target.short_description = "Target"
    
    def get_completion(self, obj):
        """Display completion percentage"""
        return f"{obj.completion_percentage}%"
    get_completion.short_description = "Completion"

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'comic', 'novel')