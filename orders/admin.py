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