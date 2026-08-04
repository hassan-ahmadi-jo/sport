from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from django.urls import reverse
import logging
from zarinpal import ZarinPal
from django.utils import timezone
from datetime import timedelta
from entitlements.models import SubscriptionEntitlement, SubscriptionOrderHistory

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


# Zarinpal
logger = logging.getLogger(__name__)

class ZarinPalConfig:
    def __init__(self):
        self.merchant_id = settings.ZARINPAL_MERCHANT_ID
        self.access_token = settings.ZARINPAL_ACCESS_TOKEN
        self.sandbox = settings.ZARINPAL_SANDBOX

def get_zarinpal_client():
    config = ZarinPalConfig()
    return ZarinPal(config)

def initiate_payment(request, order):
    try:
        zarinpal = get_zarinpal_client()


        callback_url = request.build_absolute_uri(reverse('payment_verify'))

        data = {
            "amount": order.total_price, 
            "callback_url": "https://zarinpal.com/", 
            "description": f"پرداخت سفارش شماره {order.id}",
            "callback_url": callback_url,
            "mobile": str(order.user.phone_number) if order.user.phone_number else '',
        }
        response = zarinpal.payments.create(data)
        
        if "data" in response and "authority" in response["data"]:
            authority = response["data"]["authority"]
            order.authority = authority 

            
            payment_url = zarinpal.payments.generate_payment_url(authority)
            return payment_url
        else:
            logger.error(f"Authority not found in response: {response.get('errors')}")
            return None

    except Exception as e:
        logger.exception(f"Error during payment creation: {e}")

def verify_payment(authority: str, amount: int, order_pk):
    try:
        zarinpal = get_zarinpal_client()  
        response = zarinpal.verifications.verify({
            "amount": int(amount),
            "authority": authority,
        })

        if not response or "data" not in response or not response["data"]:
            logger.error(f"ZarinPal invalid response structure for Authority: {authority}")
            return False, "ZARINPAL_ERROR"

        data = response.get('data') if response else None
        if data:
            code = data.get('code')
            ref_id = data.get('ref_id')
        else:
            return False, "ZARINPAL_ERROR"

        if code in [100, 101]:
            with transaction.atomic():
                order = models.Order.objects.select_for_update().get(pk=order_pk)
                if order.status != order.STATUS_PAID:
                    order.ref_id = ref_id
                    order.status = order.STATUS_PAID
                    order.save()
                return True, str(ref_id)
        else:
            with transaction.atomic():
                order = models.Order.objects.select_for_update().get(pk=order_pk)
                if order.status != order.STATUS_PAID:
                    order.status = order.STATUS_FAILED
                    order.save()
                logger.warning(f"Transaction failed with code {code} for Authority: {authority}")
                return False, code or 'UNKNOWN'

    except models.Order.DoesNotExist:
        logger.error(f"Order not found for authority verification: {authority}")
        return False, "ORDER_NOT_FOUND"

    except Exception as e:
        logger.exception(f"Payment Verification Error: {e}")
        return False, "GATEWAY_ERROR"


@transaction.atomic
def add_subscription_to_user(user_id, order_item_id):
    try:
        user = User.objects.select_for_update().get(id=user_id)
        order_item = models.OrderSubscriptionItem.objects.select_related('order', 'package', 'package__product').select_for_update().get(
            id=order_item_id,
            order__user__id = user_id,
            order__status = models.Order.STATUS_PAID
            )
        
    except User.DoesNotExist:
        logger.warning(
            'Subscription activation failed: user does not exist. user_id=%s',
            user_id,
        )
        return False

    except models.OrderSubscriptionItem.DoesNotExist:
        logger.warning(
            'Subscription activation failed: invalid or unpaid order item. '
            'user_id=%s, order_item_id=%s',
            user_id,
            order_item_id,
        )
        return False
    now = timezone.now()
    if not SubscriptionOrderHistory.objects.filter(order_item=order_item).exists() and not order_item.subscriptions_activated:
        product = order_item.package.product
        try:
            entitlement = SubscriptionEntitlement.objects.select_for_update().get(user=user, product=product)
        except SubscriptionEntitlement.DoesNotExist:
            entitlement = SubscriptionEntitlement.objects.create(user=user, product=product)

        expires_at = entitlement.expires_at 
        duration_days = timedelta(days=order_item.package.duration_days)
        if expires_at is None or expires_at < now:
            entitlement.expires_at = now + duration_days
        else:
            entitlement.expires_at = expires_at + duration_days
        entitlement.save(update_fields = ['expires_at'])
        SubscriptionOrderHistory.objects.create(
            entitlement = entitlement,
            order_item = order_item
        )
        order_item.subscriptions_activated = True
        order_item.subscriptions_activated_at = now
        order_item.save(update_fields = ['subscriptions_activated', 'subscriptions_activated_at'])
        return True
    return False

@transaction.atomic
def remove_user_cart_item(user_id, order_item_id):
    order_item = models.OrderSubscriptionItem.objects.select_related('order', 'package', 'package__product').select_for_update().get(id=order_item_id)
    cart_items = models.CartSubscriptionItem.objects.select_related('cart', 'cart__user', 'package', 'package__product').select_for_update().filter(
        cart__user__id=user_id,
        package=order_item.package
        ).all()
    for cart_item in cart_items:
        cart_item.delete()