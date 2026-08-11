from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.views.generic import TemplateView, DetailView
from . import models
from entitlements.models import SubscriptionEntitlement

# Create your views here.

class SubscriptionProductDetailView(DetailView):
    template_name = 'products/subscription_product_detail.html'
    model = models.SubscriptionProduct
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('packages').select_related('active_course_config__current_course').filter(active_course_config__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        product = self.object
        entitlement = SubscriptionEntitlement.objects.filter(user__id=user_id, product=product).first()
        context['entitlement'] = entitlement
        config_obj = getattr(product, 'active_course_config', None)
        if config_obj and config_obj.current_course:
            context['course'] = config_obj.current_course
        else:
            raise Http404
        return context