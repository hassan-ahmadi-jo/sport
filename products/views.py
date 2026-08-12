from django.shortcuts import render
from django.http import Http404
from django.views.generic import DetailView, ListView
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

class ProductsView(ListView):
    template_name = 'products/products.html'
    model = models.SubscriptionProduct
    context_object_name = 'products'

    def get_queryset(self):
        qs = (super().get_queryset()
            .prefetch_related('packages')
            .select_related('active_course_config', 'active_course_config__current_course')
            .filter(
            is_active = True,
            active_course_config__isnull = False,
            active_course_config__current_course__isnull = False
        ))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = context['products']
        for product in products:
            packages = product.packages.filter(is_active = True)
            product.active_packages_count = packages.count()
            product.min_price = packages.order_by('price').first().price
            config = getattr(product, 'active_course_config', None)
            if config and config.current_course:
                course = config.current_course
                product.next_update_days = course.next_update_days
                product.course_slug = course.slug
                print(course.slug)
        return context