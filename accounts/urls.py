from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify/', views.AccountActivationView.as_view(), name='verify'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('password/forgot', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('password/forgot/verify', views.VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('password/forgot/set', views.SetNewPasswordView.as_view(), name='set_new_password'),
    path('', views.profileView.as_view(), name='profile'),
]
