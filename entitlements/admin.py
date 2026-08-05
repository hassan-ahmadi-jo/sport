from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.SubscriptionEntitlement)
class SubscriptionEntitlementAdmin(admin.ModelAdmin):
    list_display = ['user', 'user__phone_number', 'product', 'is_active', 'remain_days']
    list_filter = ['user__phone_number', 'product__title']
    search_fields = ['user', 'user__phone_number', 'product', 'is_active']

@admin.register(models.SubscriptionOrderHistory)
class SubscriptionOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['entitlement', 'order_item', 'date']
    list_filter = ['entitlement__user__phone_number', 'order_item__package_title', 'order_item__product_title']
    search_fields = ['entitlement__user__phone_number', 'order_item__package_title', 'order_item__product_title']