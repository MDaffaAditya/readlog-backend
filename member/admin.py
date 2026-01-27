from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from member.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name') 
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': () 
        }),
    )