from django.urls import path
from . import views

urlpatterns = [
    path('<str:slug>/day/<int:day_id>/', views.WorkoutDayDetailView.as_view(), name='workout_day_detail'),
    path('<str:slug>/', views.WorkoutCourseView.as_view(), name='workout_course'),
]
