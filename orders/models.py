from django.db import models
from accounts.models import User
from products.models import SubscriptionPackage

# Create your models here.

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='user')

    @property
    def total_price(self):
        price = 0
        for item in self.subscription_items.all():
            price += item.price
        return price

    
    @property
    def tax_amount(self):
        return int(self.total_price * 0.10)

    @property
    def payable_amount(self):
        return self.total_price + self.tax_amount

    def add_subscription_package(self, package):
        product = package.product

        existing_item = self.subscription_items.select_related("package__product").filter(
            package__product=product
        ).first()

        if existing_item:
            if existing_item.package_id == package.id:
                return existing_item
            existing_item.delete()

        return self.subscription_items.create(package=package)
    
    class Meta:
        verbose_name = 'سبد خرید کاربر'
        verbose_name_plural = 'سبد خرید کاربرها'

    def __str__(self):
        text = 'سبد خرید '
        if self.user.first_name:
            text += self.user.first_name
        else:
            text += str(self.user.phone_number)
        return text

class CartSubscriptionItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='subscription_items', verbose_name='سبد خرید')
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE, related_name='carts', verbose_name='محصول')

    @property
    def price(self):
        return self.package.price
        
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['cart', 'package'],
                name = 'unique_cart_package'
            )
        ]
        verbose_name = 'آیتم خرید'
        verbose_name_plural = 'آیتم های خرید'

    def __str__(self):
        if self.cart.user.first_name:
            user = self.cart.user.first_name
        else:
            user = str(self.cart.user.phone_number)
        return f'{user} - {self.package.title}'
