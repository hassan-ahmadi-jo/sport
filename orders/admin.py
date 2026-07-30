from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user__first_name', 'user__phone_number', ]

@admin.register(models.CartSubscriptionItem)
class CartSubscriptionItemAdmin(admin.ModelAdmin):
    list_display = ['cart__user__phone_number', 'package__title', 'package__product__title', 'price']
    list_filter = ['cart__user__phone_number', 'package__title', 'package__product__title']
    search_fields = ['cart__user__phone_number', 'package__title', 'package__product__title']

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user__phone_number', 'status', 'tracking_code', 'total_price', 'created_at']
    list_filter = ['user__phone_number', 'status']
    search_fields = ['user__phone_number', 'status', 'tracking_code', 'total_price', 'created_at']

@admin.register(models.OrderSubscriptionItem)
class OrderSubscriptionItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'order__status', 'package_title', 'product_title', 'price']
    list_filter = ['order', 'order__user', 'order__status', 'package_title', 'product_title']
    search_fields = ['order', 'order__status', 'package_title', 'product_title']