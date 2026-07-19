from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from secrets import randbelow
from django.utils import timezone
from datetime import timedelta
import random
from . import models

def send_security_code(code):
    print('****************')
    print('****************')
    print('')
    print(f'Security code is: {code}')
    print('')
    print('****************')
    print('****************')


def generate_security_code(user = None):
    length = max(int(settings.SECURITY_CODE_LENGTH), 4)
    start = 10 ** (length - 1)
    end = 10 ** length
    code = str(start + randbelow(end - start))
    if user and hasattr(user, 'otp'):
        while check_password(code, user.otp.security_code):
            code = str(start + randbelow(end - start))
    return code

def generate_retry_time(failed_attempts):
    limit = settings.SECURITY_CODE_MAX_FAILED_ATTEMPTS
    base_penalty_time = 2 * 60 # 2 minutes
    if failed_attempts % limit == 0:
        if failed_attempts <= limit * 2:
            return int(base_penalty_time * (failed_attempts / limit))
        elif failed_attempts < limit * 6:
            return int(base_penalty_time * (failed_attempts / limit)) * 3
        return 24 * 60 * 60
    return -1

def security_code_handler(user: models.User, action:str, user_otp_code = None):
    now = timezone.now()

    if not user:
        raise ValueError('User not found')

    if action == 'create':
        code = generate_security_code()
        models.OTPChallenge.objects.get_or_create(
            user = user,
            defaults={
                'security_code': make_password(code),
                'expires_at': now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES),
                'next_retry_at': now - timedelta(minutes=1),
                'next_resend_at': now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
                }
            )
        send_security_code(code)
        return True
    
    if action == 'check':
        if user_otp_code is None:
            raise ValueError('User OTP code is None, please enter OTP code')
        
        if not hasattr(user, 'otp'):
            raise ValueError('This user has no otp')
        
        user_otp_code = str(user_otp_code)
        otp = user.otp
        if otp.next_retry_at > now:
            return False, (otp.next_retry_at - now).total_seconds(), -1
        
        if otp.expires_at < now:
            return False, (otp.next_retry_at - now).total_seconds(), -1
        
        is_code_correct = check_password(user_otp_code, otp.security_code)
        if is_code_correct:
            otp.failed_attempts = 0
            otp.next_retry_at = now - timedelta(minutes=1)
            otp.expires_at = now - timedelta(minutes=1)
            otp.save()
            return True, -1, -1
        else:
            failed_attempts = otp.failed_attempts
            penalty_time = generate_retry_time(failed_attempts)
            otp.failed_attempts = failed_attempts + 1
            if penalty_time > 0:
                otp.next_retry_at = now + timedelta(seconds=penalty_time)
                otp.expires_at = now - timedelta(minutes=1)
            otp.save()
            return False, penalty_time, (otp.expires_at - now).total_seconds()
    
    if action == 'resend':
        if not hasattr(user, 'otp'):
            raise ValueError('This user has no otp')
        
        otp = user.otp
        if now > max(otp.next_resend_at, otp.next_retry_at):
            failed_attempts = otp.failed_attempts
            new_failed_attempts = failed_attempts - (failed_attempts % settings.SECURITY_CODE_MAX_FAILED_ATTEMPTS)
            code = generate_security_code(user)
            otp.next_resend_at = now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
            otp.security_code = make_password(code)
            otp.expires_at = now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES)
            otp.failed_attempts = new_failed_attempts + 1
            otp.save()
            send_security_code(code)
            return True
        else:
            return False
    
    if action == 'get_data':
        otp = getattr(user, 'otp', None)
        if otp:
            next_retry = (otp.next_retry_at - now).total_seconds()
            next_resend = (otp.next_resend_at - now).total_seconds()
            expire = (otp.expires_at - now).total_seconds()
        else:
            next_retry = -1
            next_resend = -1
            expire = -1
        return next_retry, next_resend, expire
    raise ValueError(f'Action must be create or check or resend or get_data. Your action is {action}')


def generate_remain_text(seconds_time: int):
    seconds = int(seconds_time % 60)
    minutes = int(((seconds_time - seconds) / 60) % 60)
    hours = int((seconds_time - 60 * minutes - seconds) / 3600)

    text_hours = ''
    text_minutes = ''
    text_seconds = ''

    if hours == 1:
        text_hours = 'یک ساعت'
    elif hours > 1:
        text_hours = f'{hours} ساعت'
    if hours and minutes:
        text_hours += ' و '
    
    if minutes == 1:
        text_minutes = 'یک دقیقه'
    elif minutes > 1:
        text_minutes = f'{minutes} دقیقه'
    if seconds and minutes and not hours:
        text_minutes += ' و '

    if seconds and not hours:
        if seconds == 1:
            text_seconds = 'یک ثانیه'
        elif seconds > 1:
            text_seconds = f'{seconds} ثانیه'
    return text_hours + text_minutes + text_seconds

def mask_phone_number(phone):
    phone = str(phone)
    return '0' + phone[3:6] + '***' + phone[9:]