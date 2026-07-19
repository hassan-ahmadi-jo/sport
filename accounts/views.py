from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import login, logout
from django.db import transaction
from django.urls import reverse_lazy
from django.http.request import HttpRequest
from . import forms, services, models

# Create your views here.

class RegisterView(UserPassesTestMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = forms.RegisterForm
    success_url = reverse_lazy('activation')
    
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('home')
    
    @transaction.atomic
    def form_valid(self, form):
        saved_form = super().form_valid(form)
        user = get_object_or_404(models.User, phone_number = form.cleaned_data.get('phone_number'))
        services.security_code_handler(user, action='create')
        self.request.session['user_id'] = user.id
        return saved_form

class AccountActivationView(UserPassesTestMixin, View):
    template_name = 'accounts/otp_verify.html'

    def get_user(self):
        if not hasattr(self, '_user'):
            user_id = self.request.session.get('user_id')
            if not user_id:
                return None
            self._user = get_object_or_404(models.User, id = user_id)
        return self._user

    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('home')

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
            services.security_code_handler(user, 'resend')
            form = forms.OTPVerifyForm(user=user)
        else:
            form = forms.OTPVerifyForm(request.POST, user=user)
            if form.is_valid():
                user.phone_verified = True
                user.save(update_fields = ['phone_verified'])
                request.session.pop('user_id', None)
                login(request, user)
                return redirect('home')
        
        return render(request, self.template_name, {'form': form, 'phone_number': phone_number})

