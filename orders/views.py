from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models, services
from products.models import SubscriptionPackage

# Create your views here.

class CartView(LoginRequiredMixin, View):
    template_name = 'orders/cart.html'

    def get(self, request):
        user = request.user
        context = {
            'cart': user.cart
        }
        return render(request, self.template_name, context=context)

    def post(self, request:HttpRequest):
        user = request.user
        remove_item_id = request.POST.get('remove')
        package_id = request.POST.get('add')
        if remove_item_id:
            subscription_item = user.cart.subscription_items.filter(id = remove_item_id)
            if subscription_item.exists():
                subscription_item.delete()
        elif package_id:
            package = get_object_or_404(SubscriptionPackage, id=package_id)
            user.cart.add_subscription_package(package)
        context = {
            'cart': user.cart
        }
        return render(request, self.template_name, context=context)

class OrderView(LoginRequiredMixin, View):
    def post(self, request:HttpRequest):
        user = self.request.user
        cart = user.cart
        services.create_order(user, cart.id)
        return redirect('cart')