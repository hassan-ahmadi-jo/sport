from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.SubscriptionProduct)
class SubscriptionProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'slug', 'is_active']
    prepopulated_fields = {"slug": ("title",)}

@admin.register(models.SubscriptionPackage)
class SubscriptionPackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'product__title', 'price', 'duration_days', 'is_active']
    list_filter = ['duration_days', 'is_active', 'product__title']
    search_fields = ['title', 'product__title', 'price', 'duration_days', 'is_active']