from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class AboutView(TemplateView):
    template_name = 'core/about.html'

class HomeView(TemplateView):
    template_name = 'core/home.html'
