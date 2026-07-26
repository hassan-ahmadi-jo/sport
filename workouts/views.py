from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.views import View
from . import models
import time

# Create your views here.

class WorkoutCourseView(DetailView):
    template_name = 'workouts/workout_course.html'
    model = models.WorkoutCourse
    context_object_name = 'course'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('subscription_product')

class WorkoutDayDetailView(View):
    template_name = 'workouts/workout_day_detail.html'
    def get(self, request, slug,day_id):
        course = get_object_or_404(models.WorkoutCourse.objects.select_related('subscription_product'), slug=slug)
        context = {
            'current_day': get_object_or_404(course.daily_workouts.all(), id=day_id)
            }
        return render(request, self.template_name, context)