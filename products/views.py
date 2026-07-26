from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from . import models

# Create your views here.

class SubscriptionProductDetailView(TemplateView):
    template_name = 'products/subscription_product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        context['product'] = get_object_or_404(models.SubscriptionProduct, slug = slug)
        return context