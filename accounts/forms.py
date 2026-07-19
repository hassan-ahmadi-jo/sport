from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError
from . import models, services

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

class OTPVerifyForm(forms.Form):
    def __init__(self, *args, user = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.next_retry_time, self.next_resend_time, self.expires_time = services.security_code_handler(user, 'get_data')

    
    otp_code = forms.CharField(
        label='کد تأیید',
        widget=forms.TextInput(attrs={
            'placeholder': '123456',
            'type': 'text', 
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'maxlength': str(max(int(settings.SECURITY_CODE_LENGTH), 6)),
            'dir': 'ltr',
            'class': 'form-control'
        })
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        
        user = self.user
        if not user:
            raise ValidationError('اطلاعات کاربر پیدا نشد.')
        
        is_code_correct, next_retry_time, expires_time = services.security_code_handler(user, 'check', otp_code)
        self.next_retry_time = next_retry_time
        self.expires_time = expires_time

        if is_code_correct:
            return otp_code

        if next_retry_time > 0:
            error_text = f'تعداد تلاش‌ها زیاد بود. لطفا {services.generate_remain_text(next_retry_time)} صبر کنید و دوباره امتحان کنید.'
            raise ValidationError(error_text)

        elif expires_time < 0:
            raise ValidationError('اعتبار این کد تمام شده است. لطفا کد جدیدی درخواست کنید.')
        

        elif not is_code_correct:
            raise ValidationError('کد وارد شده صحیح نیست. لطفا دوباره بررسی کنید.')
        

        return otp_code
    
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='تلفن تماس',
        widget=forms.TextInput(attrs={
                "autofocus": True,
                'class': 'form-control',
                'placeholder': '09123456789',
                'type': 'tel',
                'dir': 'ltr',
                'inputmode': 'numeric',
            })
        )
    password = forms.CharField(
        label='گذرواژه',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            'class': 'form-control',
            'dir': 'ltr',
            }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username[0] == '0':
            username = username[1:]
        username = '+98' + username

        return username