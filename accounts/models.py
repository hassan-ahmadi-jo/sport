from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.hashers import make_password

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=200, verbose_name='نام و نام خانوادگی')
    phone_number = PhoneNumberField(unique=True, blank=False, null=False, max_length=150, verbose_name='تلفن تماس')
    phone_verified = models.BooleanField(default=False, verbose_name='تلفن تماس معتبر است؟')
    REQUIRED_FIELDS = ['phone_number']
    def save(self, *args, **kwargs):
        self.username = self.phone_number
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.first_name

class OTPChallenge(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp', verbose_name='کاربر')
    security_code = models.CharField(max_length=128, unique=True, verbose_name='هش کد تأیید')
    expires_at = models.DateTimeField(verbose_name='زمان انقضا')
    next_retry_at = models.DateTimeField(verbose_name='تا این زمان اجازه تلاش مجدد ندارد')
    next_resend_at = models.DateTimeField(verbose_name='زمان مجاز بعدی برای ارسال مجدد')
    failed_attempts = models.IntegerField(default=0, verbose_name='تعداد تلاش‌های ناموفق')

    def __str__(self):
        return str(self.user.phone_number)
    