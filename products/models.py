from django.db import models
from django.utils.text import slugify
from sports.utils.slug import unique_slug_generator

# Create your models here.

# Subscription Products

class SubscriptionProduct(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='عنوان در آدرس')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    image = models.ImageField(blank=True, null=True, upload_to='images/subscription_products', verbose_name='تصویر (عرض دو برابر ارتفاع)')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'محصول اشتراکی'
        verbose_name_plural = 'محصولات اشتراکی'

    def __str__(self):
        return self.title

class SubscriptionPackage(models.Model):
    product = models.ForeignKey(SubscriptionProduct, related_name='packages', on_delete=models.CASCADE, verbose_name='محصول')
    title = models.CharField(max_length=150, verbose_name='عنوان پکیج (برای مثال: ۳ ماهه طلایی)')
    price = models.PositiveIntegerField(verbose_name='مبلغ نهایی (تومان)')
    price_without_discount = models.PositiveIntegerField(blank=True, null=True, verbose_name='مبلغ بدون تخفیف')
    duration_days = models.PositiveIntegerField(verbose_name='تعداد روزهای اشتراک')
    is_active = models.BooleanField(default=False, verbose_name='فعال است؟')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'پکیج قیمتی برای محصول اشتراکی'
        verbose_name_plural = 'پکیج های قیمتی برای محصول اشتراکی'

    def __str__(self):
        return self.title

    @property
    def has_discount(self):
        return self.price_without_discount is not None and self.price_without_discount > self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            discount = self.price_without_discount - self.price
            return int((discount / self.price_without_discount) * 100)
        return 0