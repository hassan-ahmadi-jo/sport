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

class PaymentOrderView(LoginRequiredMixin, View):
    def post(self, request:HttpRequest):
        user = self.request.user
        cart = user.cart
        order = services.create_order(user, cart.id)
        payment_url = services.initiate_payment(request, order)
        if payment_url:
            return redirect(payment_url)
        return redirect('cart')
        # return render(request, 'error.html', {'message': 'خطا در درگاه'})

class PaymentVerifyView(LoginRequiredMixin, View):
    template_name = 'orders/payment_verify.html'
    
    def get(self, request:HttpRequest):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')
        order = None
        if not authority:
            success = False
            message = 'AUTHORITY_NOT_VALID'
        elif status != 'OK':
            success = False
            message = 'STATUS_NOT_OK'
        else:
            order = get_object_or_404(models.Order.objects.select_related('user'), authority=authority, user__id=request.user.id)
            success, message = services.verify_payment(authority, order.total_price, order.pk)
            # TODO: Add Subscription to user and check if its the first time
        context = {
            'success': success,
            'message': message,
        }
        if order:
            context['order'] = order
        return render(request, self.template_name, context)