from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from . import forms

# Create your views here.

class RegisterView(UserPassesTestMixin, CreateView):
    template_name = 'accounts/register.html'
    form_class = forms.RegisterForm
    success_url = reverse_lazy('home')
    
    def test_func(self):
        return not self.request.user.is_authenticated
    
    def handle_no_permission(self):
        return redirect('home')
