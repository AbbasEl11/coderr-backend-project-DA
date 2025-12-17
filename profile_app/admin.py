from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Profile model."""
    
    list_display = ['user', 'type', 'first_name', 'last_name', 'location', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name']
    readonly_fields = ['created_at']

# Register your models here.
