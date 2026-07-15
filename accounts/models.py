from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField 

# Create your models here.

class User(AbstractUser):
    first_name = models.CharField(max_length=200, verbose_name='نام و نام خانوادگی')
    phone_number = PhoneNumberField(unique=True, blank=False, null=False, max_length=150, verbose_name='تلفن تماس')
    REQUIRED_FIELDS = ['phone_number']
    def save(self, *args, **kwargs):
        self.username = self.phone_number
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.first_name