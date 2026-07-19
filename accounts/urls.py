from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('activate/', views.AccountActivationView.as_view(), name='activation'),
    path('', views.RegisterView.as_view(), name='home'),

]
