from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings
from django.urls import reverse
import logging
from zarinpal import ZarinPal

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