from django.urls import path
from . import views

urlpatterns = [
    path('', views.WorkoutClubView.as_view(), name='workout_club'),
    path('day/<int:day_id>/', views.WorkoutDayDetailView.as_view(), name='workout_day_detail')
]
