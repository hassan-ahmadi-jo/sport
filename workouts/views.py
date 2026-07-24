from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.views import View
from . import models
import time

# Create your views here.

class WorkoutClubView(TemplateView):
    template_name = 'workouts/workout_club.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = models.WorkoutCourse.objects.first()
        context['course'] = course
        return context

class WorkoutDayDetailView(View):
    template_name = 'workouts/workout_day_detail.html'
    def get(self, request, day_id):
        course = models.WorkoutCourse.objects.first()
        context = {
            'current_day': get_object_or_404(course.daily_workouts, id=day_id)
            }
        return render(request, self.template_name, context)