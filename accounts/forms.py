from django import forms
from django.contrib.auth.forms import UserCreationForm
from . import models

class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        label= 'گذرواژه',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'حداقل 8 کاراکتر'
            }),
    )
    password2 = forms.CharField(
        label='تأیید گذرواژه',
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'گذرواژه را مجدد وارد کنید'
            }),
        strip=False,
    )
    class Meta:
        model = models.User
        fields = ['first_name', 'phone_number', 'password1', 'password2']

        labels = {
            'first_name': 'نام و نام خانوادگی',
            'phone_number': 'تلفن تماس',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':  'سارا فرهمند'
            }),

            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09123456789',
                'type': 'tel',
                'dir': 'ltr',
                'inputmode': 'numeric',
            }),
        }
    