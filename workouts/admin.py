from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.WorkoutCourse)
class WorkoutCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'start_date', 'duration_days']
    list_filter = ['duration_days', 'start_date']
    search_fields = ['number', 'title']
    prepopulated_fields = {"slug": ("title",)}

    ordering = ['number']

@admin.register(models.DailyWorkout)
class DailyWorkoutAdmin(admin.ModelAdmin):
    list_display = ['plan', 'day_number', 'title']
    list_filter = ['plan']
    search_fields = ['plan__number', 'title']
    
    ordering = ['plan__number', 'day_number']