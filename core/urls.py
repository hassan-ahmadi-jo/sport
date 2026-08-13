from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('', views.HomeView.as_view(), name='home'),
]