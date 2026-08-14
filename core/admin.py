from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'email', 'instagram', 'telegram', 'whatsapp']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'is_active', 'email', 'instagram', 'telegram', 'whatsapp']
