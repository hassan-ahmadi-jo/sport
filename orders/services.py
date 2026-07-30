from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import User
from . import models

@transaction.atomic
def create_order(user, cart_id):
    cart = get_object_or_404(models.Cart.objects.select_for_update(), id = cart_id, user=user)
    cart_items = cart.subscription_items.select_related('package', 'package__product')

    if not cart_items.exists():
        raise ValidationError('Cart items is empty')

    order = models.Order.objects.create(
        user = user,
        no_tax_amount = cart.total_price,
        total_price = cart.payable_amount,
    )

    order_items = []
    for item in cart_items.all():
        order_items.append(
            models.OrderSubscriptionItem(
                order = order,
                package = item.package,
                package_title = item.package.title,
                product_title = item.package.product.title,
                price = item.package.price,
        ))

    models.OrderSubscriptionItem.objects.bulk_create(order_items)

    return order