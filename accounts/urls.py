from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # accounts
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    path('accounts/verify/', views.AccountActivationView.as_view(), name='verify'),
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/password/forgot/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('accounts/password/forgot/verify/', views.VerifyResetOTPView.as_view(), name='verify_reset_otp'),
    path('accounts/password/forgot/set/', views.SetNewPasswordView.as_view(), name='set_new_password'),

    # profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/dashboard/', views.ProfileDashboardView.as_view(), name='profile_dashboard'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
]
