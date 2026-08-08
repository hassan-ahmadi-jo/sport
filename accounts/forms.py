from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.conf import settings
from django.core.exceptions import ValidationError
from . import models, services

class RegisterForm(UserCreationForm):
    def __init__(self, *args, account_lookup_allowed = True, **kwargs):
        self.account_lookup_allowed = account_lookup_allowed
        super().__init__(*args, **kwargs)

    password1 = forms.CharField(
        label= 'گذرواژه',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'حداقل 8 کاراکتر'
            }),
        error_messages={
            'required': 'گذرواژه اجباری است.'
        }
    )
    password2 = forms.CharField(
        label='تأیید گذرواژه',
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'گذرواژه را مجدد وارد کنید'
            }),
        strip=False,
        error_messages={
                'required': 'تأیید گذرواژه اجباری است.'
            }
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

        error_messages = {
            'first_name': {'required': 'نام و نام خانوادگی اجباری است',
                           'max_length': 'نام و نام خانوادگی نباید بیشتر از 200 کارکتر باشد'},
            'phone_number': {
                'required': 'تلفن تماس ضروری است'
            },
        }

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name')
        if len(name) < 3:
            raise ValidationError('نام و نام خوانوادگی نباید کمتر از 3 کاراکتر باشد')
        return name
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if self.account_lookup_allowed is False:
            raise ValidationError('تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً تلاش کنید.')
        elif models.User.objects.filter(phone_number = phone).exists():
            raise ValidationError('این شماره موبایل قبلاً ثبت شده است. لطفاً وارد حساب خود شوید یا رمز عبورتان را بازیابی کنید.')
        return phone

class OTPVerifyForm(forms.Form):
    def __init__(self, *args, user = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.next_retry_time, self.next_resend_time, self.expires_time = services.get_otp_code_date(user)

    
    otp_code = forms.CharField(
        label='کد تأیید',
        widget=forms.TextInput(attrs={
            'placeholder': '123456',
            'type': 'text', 
            'inputmode': 'numeric',
            'pattern': '[0-9]*',
            'maxlength': str(max(int(settings.SECURITY_CODE_LENGTH), 4)),
            'dir': 'ltr',
            'class': 'form-control'
        }),
        error_messages={
            'required': 'وارد کردن کد تأیید ضروری است.'
        }
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        
        user = self.user
        if not user:
            raise ValidationError('اطلاعات کاربر پیدا نشد.')
        
        is_code_correct, next_retry_time, expires_time = services.check_otp_code(user, otp_code)
        self.next_retry_time = next_retry_time
        self.expires_time = expires_time

        if is_code_correct:
            return otp_code

        if next_retry_time > 0:
            error_text = 'تعداد تلاش‌های ناموفق بیش از حد مجاز است. پس از پایان زمان انتظار، کد جدیدی درخواست کنید.'
            
            raise ValidationError(error_text)

        elif expires_time < 0:
            raise ValidationError('اعتبار این کد تمام شده است. لطفا کد جدیدی درخواست کنید.')
        

        elif not is_code_correct:
            raise ValidationError('کد وارد شده صحیح نیست. لطفا دوباره بررسی کنید.')
        

        return otp_code
    
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='شماره موبایل خود را وارد کنید',
        widget=forms.TextInput(attrs={
                "autofocus": True,
                'class': 'form-control',
                'placeholder': '09123456789',
                'type': 'tel',
                'dir': 'ltr',
                'inputmode': 'numeric',
            }),
            error_messages={
                'required': 'شماره موبایل ضروری است.'
            }
        )
    password = forms.CharField(
        label='گذرواژه',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            'class': 'form-control',
            'dir': 'ltr',
            }),
            error_messages={
                'required': 'گذرواژه ضروری است.'
            }
    )

    def clean_username(self):
        phone_number = self.cleaned_data.get('username')
        is_valid, normalize_phone_number = services.normalize_phone_number(phone_number)
        if not is_valid:
            raise ValidationError('شماره موبایل واردشده معتبر نیست.')
        return normalize_phone_number

    
class ForgotPasswordForm(forms.Form):
    phone_number = forms.CharField(
        label='شماره موبایل خود را وارد کنید',
        widget=forms.TextInput(attrs={
                "autofocus": True,
                'class': 'form-control',
                'placeholder': '09123456789',
                'type': 'tel',
                'inputmode': 'numeric',
            }),
            error_messages={
                'required': 'شماره موبایل ضروری است.'
            }
        )
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        is_valid, normalize_phone_number = services.normalize_phone_number(phone_number)
        if not is_valid:
            raise ValidationError('شماره موبایل واردشده معتبر نیست.')
        return normalize_phone_number
    
class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=  'گذرواژه جدید',
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'حداقل 8 کاراکتر',
            }),
            error_messages={
            'required': 'گذرواژه اجباری است.'
        }
    )
    new_password2 = forms.CharField(
        label='تأیید گذرواژه جدید',
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'form-control',
            'placeholder': 'گذرواژه را مجدد وارد کنید',
            }),
        strip=False,
        error_messages={
                'required': 'تأیید گذرواژه اجباری است.'
            }
    )

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ['first_name', 'last_name']

        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی'
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'profile-edit-form-control',
                'placeholder':  'مثال: سارا'
            }),
            'last_name': forms.TextInput(attrs={
                            'class': 'profile-edit-form-control',
                            'placeholder':  'مثال: فرهمند'
                        }),
            }

        error_messages = {
            'first_name': {'required': 'نام اجباری است',
                            'max_length': 'نام نباید بیشتر از 200 کارکتر باشد'},
            'last_name': {'max_length': 'نام خانوادگی نباید بیشتر از 200 کارکتر باشد'},
        }

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name')
        if len(name) < 3:
            raise ValidationError('نام نباید کمتر از 3 کاراکتر باشد')
        return name

    