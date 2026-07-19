from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'phone_number']
    search_fields = ['first_name', 'phone_number']

@admin.register(models.OTPChallenge)
class OPTAdmin(admin.ModelAdmin):
    list_display  = ['user__first_name', 'user__phone_number']
    search_fields = ['user__first_name', 'user__phone_number']