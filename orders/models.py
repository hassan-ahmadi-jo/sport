from django.db import models, transaction, IntegrityError
from django.core.exceptions import ValidationError
from accounts.models import User
from products.models import SubscriptionPackage
import string
import secrets
# Create your models here.

def generate_order_tracking_code(user_id, user_order_index, length):
    allowed_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits * 3
    allowed_chars = ''.join(c for c in allowed_chars if c not in '01OILl') 
    random_suffix = ''.join(secrets.choice(allowed_chars) for _ in range(length))
    return f'{user_id}-{user_order_index}-{random_suffix}'

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

    def clean(self):
        super().clean()
        if not (self.package.is_active or self.package.product.is_active):
            raise ValidationError('امکان افزودن پکیج یا محصول غیرفعال به سبد خرید وجود ندارد.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
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


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار پرداخت'),
        (STATUS_PAID, 'پرداخت شده'),
        (STATUS_FAILED, 'پرداخت ناموفق'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='کاربر')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='وضعیت')

    tracking_code = models.CharField(max_length=70, blank=True, null=True, unique=True, editable=False, verbose_name='کد پیگیری داخلی')

    no_tax_amount = models.PositiveIntegerField(verbose_name='مبلغ بدون مالیات')
    total_price = models.PositiveIntegerField(verbose_name='مبلغ نهایی')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='زمان بروزرسانی')

    authority = models.CharField(db_index=True, max_length=255, blank=True, null=True, verbose_name='authority درگاه')
    ref_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ref id درگاه')

    def save(self, *args, **kwargs):
        if self.tracking_code:
            return super().save(*args, **kwargs)

        user_order_index = Order.objects.filter(user__id=self.user.id).count() + 1
        for _ in range(10):  # retry limit
            self.tracking_code = generate_order_tracking_code(self.user.id, user_order_index, 4)
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.tracking_code = None


    @property
    def tax_amount(self):
        return self.total_price - self.no_tax_amount

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'

    def __str__(self):
        return f'سفارش {self.id} - {self.user}'


class OrderSubscriptionItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='subscription_items', verbose_name='سفارش')
    package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE, related_name='order_items', verbose_name='پکیج')

    package_title = models.CharField(max_length=200, verbose_name='عنوان پکیج')
    product_title = models.CharField(max_length=200, verbose_name='عنوان محصول')
    price = models.PositiveIntegerField(verbose_name='قیمت خرید')

    subscriptions_activated = models.BooleanField(default=False, verbose_name='اشتراک فعال شده است؟')
    subscriptions_activated_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان فعال‌سازی اشتراک")

    class Meta:
        verbose_name = 'آیتم خرید سفارش'
        verbose_name_plural = 'آیتم‌های خرید سفارش'

    def __str__(self):
        return f'{self.product_title} - {self.package_title}'

    def save(self, *args, **kwargs):
        if not self.package_title:
            self.package_title = self.package.title
        if not self.product_title:
            self.product_title = self.package.product.title
        if not self.price:
            self.price = self.package.price
        return super().save(*args, **kwargs)
