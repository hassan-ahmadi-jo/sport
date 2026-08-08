from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth import login, logout
from django.db import transaction
from django.urls import reverse_lazy
from django.http.request import HttpRequest
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from . import forms, services, models
import time

# Create your views here.

class RegisterView(UserPassesTestMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = forms.RegisterForm
    success_url = reverse_lazy('verify')
    
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')
    
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        if not services.consume_account_lookup_attempt(self.request.session):
            form_kwargs['account_lookup_allowed'] = False
        return form_kwargs
    
    @transaction.atomic
    def form_valid(self, form):
        if not services.consume_account_lookup_attempt(self.request.session):
            form.add_error('phone_number', 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')
            return self.form_invalid(form)
        saved_form = super().form_valid(form)
        user = get_object_or_404(models.User, phone_number = form.cleaned_data.get('phone_number'))
        send_message, security_code = services.create_otp_code(user)
        if send_message:
            services.send_security_code(security_code)
        self.request.session['account_activation_user_id'] = user.id
        return saved_form

class AccountActivationView(UserPassesTestMixin, View):
    template_name = 'accounts/otp_verify.html'

    def get_user(self):
        if not hasattr(self, '_user'):
            user_id = self.request.session.get('account_activation_user_id')
            if not user_id:
                return None
            self._user = get_object_or_404(models.User, id = user_id)
        return self._user

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')

    def get(self, request: HttpRequest):
        user = self.get_user()
        if not user:
            return redirect('register') # redirect to login page
        phone_number = services.mask_phone_number(user.phone_number)
        context = {'form': forms.OTPVerifyForm(user=user),
                    'phone_number': phone_number}
        return render(request, self.template_name, context)
    

    def post(self, request:HttpRequest):
        user = self.get_user()
        if not user:
            return redirect('register') # redirect to login page
        

        phone_number = services.mask_phone_number(user.phone_number)

        if request.POST.get('action') == 'resend':
            send_message, security_code = services.resend_otp_code(user)
            if send_message:
                services.send_security_code(security_code)
            form = forms.OTPVerifyForm(user=user)
        else:
            form = forms.OTPVerifyForm(request.POST, user=user)
            if form.is_valid():
                user.phone_verified = True
                user.save(update_fields = ['phone_verified'])
                request.session.pop('account_activation_user_id', None)
                login(request, user)
                return redirect('profile')
        
        return render(request, self.template_name, {'form': form, 'phone_number': phone_number})


class UserLoginView(UserPassesTestMixin, LoginView):
    template_name = 'accounts/login.html'
    form_class = forms.UserLoginForm

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')

    def form_valid(self, form):
        user = form.get_user()
        if not user.phone_verified:
            self.request.session['account_activation_user_id'] = user.id
            send_message, security_code = services.resend_otp_code(user)
            if send_message:
                services.send_security_code(security_code)
            return redirect('verify')
        return super().form_valid(form)

class ProfileView(LoginRequiredMixin ,TemplateView):
    template_name = 'accounts/profile/base.html'

    
class ForgotPasswordView(UserPassesTestMixin, View):
    template_name = 'accounts/forgot_password.html'

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')
    
    def get(self, request):
        form = forms.ForgotPasswordForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request:HttpRequest):
        form = forms.ForgotPasswordForm(request.POST)

        if not services.consume_account_lookup_attempt(request.session):
            form.add_error('phone_number', 'تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')

        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            self.request.session['phone_number'] = phone_number
            user = models.User.objects.filter(phone_number=phone_number).first()
            if user is not None:
                if models.OTPChallenge.objects.filter(user=user).exists():
                    send_message, security_code = services.resend_otp_code(user)
                    if send_message:
                        services.send_security_code(security_code)
                else:
                    send_message, security_code = services.create_otp_code(user)
                    if send_message:
                        services.send_security_code(security_code)
                return redirect('verify_reset_otp')
        return render(request, self.template_name, {'form': form})
    


class VerifyResetOTPView(UserPassesTestMixin, View):
    template_name = 'accounts/otp_verify.html'

    def get_user(self):
        if not hasattr(self, '_user'):
            self.phone_number = self.request.session.get('phone_number')
            self._user = models.User.objects.filter(phone_number=self.phone_number).first()
        return self._user

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')

    def get(self, request: HttpRequest):
        user = self.get_user()
        if self.phone_number is None:
            return redirect('login')
        phone_number = services.mask_phone_number(self.phone_number)
        context = {'form': forms.OTPVerifyForm(user=user),
                    'phone_number': phone_number}
        return render(request, self.template_name, context)
    

    def post(self, request:HttpRequest):
        user = self.get_user()
        if self.phone_number is None:
            return redirect('login')
        

        phone_number = services.mask_phone_number(self.phone_number)

        if request.POST.get('action') == 'resend':
            send_message, security_code = services.resend_otp_code(user)
            if send_message:
                services.send_security_code(security_code)
            form = forms.OTPVerifyForm(user=user)
        else:
            form = forms.OTPVerifyForm(request.POST, user=user)
            if form.is_valid():
                request.session.pop('phone_number', None)
                request.session['password_reset_user_id'] = user.id
                request.session['password_reset_expires_at'] = (timezone.now() + timedelta(minutes=settings.PASSWORD_RESET_SESSION_TIMEOUT)).isoformat()
                return redirect('set_new_password')
        
        return render(request, self.template_name, {'form': form, 'phone_number': phone_number})
    
class SetNewPasswordView(UserPassesTestMixin, View):
    template_name = 'accounts/set_new_password.html'
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('profile')
    
    def get(self, request:HttpRequest):
        user_id = request.session.get('password_reset_user_id')
        if user_id is None:
            return redirect('login')
        user = get_object_or_404(models.User, id=user_id)
        form = forms.SetNewPasswordForm(user=user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request:HttpRequest):
        user_id = request.session.get('password_reset_user_id')
        expires_at_string = request.session.get('password_reset_expires_at')
        if not user_id or not expires_at_string:
            return redirect('login')
        try:
            password_reset_expires_at = datetime.fromisoformat(expires_at_string)
        except (TypeError, ValueError):
            return redirect('login')
        
        if user_id is None:
            return redirect('login')
        user = get_object_or_404(models.User, id=user_id)

        form = forms.SetNewPasswordForm(data=request.POST, user=user)
        if password_reset_expires_at < timezone.now():
            request.session.pop('password_reset_user_id', None)
            request.session.pop('password_reset_expires_at', None)
            form.add_error('new_password2', 'مهلت تعیین رمز عبور جدید به پایان رسیده است. لطفاً دوباره مراحل بازیابی رمز را انجام دهید.')
        if form.is_valid():
            form.save()
            request.session.pop('password_reset_user_id', None)
            request.session.pop('password_reset_expires_at', None)
            return redirect('login')
        return render(request, self.template_name, {'form': form})

class ProfileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile/dashboard.html'
