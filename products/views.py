from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DeleteView
from . import models
from entitlements.models import SubscriptionEntitlement

# Create your views here.

class SubscriptionProductDetailView(DeleteView):
    template_name = 'products/subscription_product_detail.html'
    model = models.SubscriptionProduct
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        product = self.get_object()
        entitlement = SubscriptionEntitlement.objects.select_related('user', 'product').filter(user__id=user_id, product=product).first()
        context['entitlement'] = entitlement
        return context