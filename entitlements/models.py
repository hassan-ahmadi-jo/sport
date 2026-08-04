from django.db import models
from django.utils import timezone

from accounts.models import User
from products.models import SubscriptionProduct
from orders.models import OrderSubscriptionItem

# Create your models here.
class SubscriptionEntitlement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_entitlements', verbose_name='کاربر')
    product = models.ForeignKey(SubscriptionProduct, on_delete=models.PROTECT, related_name='subscription_entitlements', verbose_name='محصول اشتراکی خریداری شده')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پایان اشتراک')

    @property
    def is_active(self):
        if self.expires_at is None:
            return False
        return self.expires_at > timezone.now()

    @property
    def remain_days(self):
        if self.is_active:
            return int((self.expires_at - timezone.now()).total_seconds() / 60 / 60 / 24) + 1
        else:
            return 0

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_user_product'
            )
        ]

        verbose_name = 'اشتراک کاربر'
        verbose_name_plural = 'اشتراک های کاربران'

    def __str__(self):
        return f'{self.user.phone_number} - {self.product.title}'

class SubscriptionOrderHistory(models.Model):
    entitlement = models.ForeignKey(SubscriptionEntitlement, on_delete=models.CASCADE, related_name='order_history', verbose_name='اشتراک')
    order_item = models.OneToOneField(OrderSubscriptionItem, on_delete=models.PROTECT, related_name='entitlement_history', verbose_name='آیتم سفارش اشتراک')

    @property
    def date(self):
        return self.order_item.subscriptions_activated_at

    class Meta:
        verbose_name = 'تاریخچه سفارش'
        verbose_name_plural = 'تاریخچه سفارشات'

    def __str__(self):
        return f'{self.entitlement.user.phone_number} - {self.order_item.package_title}'