from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from secrets import randbelow
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
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

@transaction.atomic
def create_otp_code(user):
    now = timezone.now()
    locked_user = (models.User.objects.select_for_update().get(pk=user.pk))

    if not user:
        return False, None
    if models.OTPChallenge.objects.filter(user=locked_user).exists():
        return False, None
    else:
        code = generate_security_code()
        models.OTPChallenge.objects.create(
            user = locked_user,
            security_code = make_password(code),
            expires_at = now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES),
            next_retry_at = now - timedelta(minutes=1),
            next_resend_at = now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
            )
    return True, code


@transaction.atomic
def check_otp_code(user, user_otp_code):
    now = timezone.now()
    if not user:
        return False, -1, 1
    
    if not hasattr(user, 'otp'):
        raise ValueError('This user has no otp')
    
    user_otp_code = str(user_otp_code)
    otp = models.OTPChallenge.objects.select_for_update().get(user=user)
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
        otp.failed_attempts = failed_attempts + 1
        penalty_time = generate_retry_time(failed_attempts)
        if penalty_time > 0:
            otp.next_retry_at = now + timedelta(seconds=penalty_time)
            otp.expires_at = now - timedelta(minutes=1)
        otp.save()
        return False, penalty_time, (otp.expires_at - now).total_seconds()

@transaction.atomic
def resend_otp_code(user):
    if not user:
        return False, None
    
    try:
        otp = models.OTPChallenge.objects.select_for_update().get(user_id=user.pk)
    except models.OTPChallenge.DoesNotExist:
        raise ValueError('This user has no OTP')
    
    now = timezone.now()
    if now > max(otp.next_resend_at, otp.next_retry_at):
        failed_attempts = otp.failed_attempts
        new_failed_attempts = failed_attempts - (failed_attempts % settings.SECURITY_CODE_MAX_FAILED_ATTEMPTS)
        code = generate_security_code(user)
        
        otp.next_resend_at = now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
        otp.security_code = make_password(code)
        otp.expires_at = now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES)
        otp.failed_attempts = new_failed_attempts + 1
        otp.save()
        return True, code
    else:
        return False, None

def get_otp_code_date(user):
    now = timezone.now()
    if not user:
        return -1, -1, -1
    otp = models.OTPChallenge.objects.filter(user=user).first()
    if otp:
        next_retry = (otp.next_retry_at - now).total_seconds()
        next_resend = (otp.next_resend_at - now).total_seconds()
        expire = (otp.expires_at - now).total_seconds()
    else:
        next_retry = -1
        next_resend = -1
        expire = -1
    return next_retry, next_resend, expire

# @transaction.atomic
# def security_code_handler(user: models.User, action:str, user_otp_code = None):

#     # if not user:
#     #     raise ValueError('User not found')

#     if action == 'create':
#         now = timezone.now()
#         if not user:
#             return False
#         if models.OTPChallenge.objects.filter(user=user).exists():
#             return False
#         else:
#             locked_user = (
#             models.User.objects
#             .select_for_update()
#             .get(pk=user.pk))
#             code = generate_security_code()
#             models.OTPChallenge.objects.create(
#                 user = locked_user,
#                 security_code = make_password(code),
#                 expires_at = now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES),
#                 next_retry_at = now - timedelta(minutes=1),
#                 next_resend_at = now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
#                 )
#             send_security_code(code)
#         return True
    
#     if action == 'check':
#         now = timezone.now()
#         if not user:
#             return False, -1, 1
        
#         if user_otp_code is None:
#             raise ValueError('User OTP code is None, please enter OTP code')
        
#         if not hasattr(user, 'otp'):
#             raise ValueError('This user has no otp')
        
#         user_otp_code = str(user_otp_code)
#         otp = models.OTPChallenge.objects.select_for_update().get(user=user)
#         if otp.next_retry_at > now:
#             return False, (otp.next_retry_at - now).total_seconds(), -1
        
#         if otp.expires_at < now:
#             return False, (otp.next_retry_at - now).total_seconds(), -1
        
#         is_code_correct = check_password(user_otp_code, otp.security_code)
#         if is_code_correct:
#             otp.failed_attempts = 0
#             otp.next_retry_at = now - timedelta(minutes=1)
#             otp.expires_at = now - timedelta(minutes=1)
#             otp.save()
#             return True, -1, -1
#         else:
#             failed_attempts = otp.failed_attempts
#             otp.failed_attempts = failed_attempts + 1
#             penalty_time = generate_retry_time(failed_attempts)
#             if penalty_time > 0:
#                 otp.next_retry_at = now + timedelta(seconds=penalty_time)
#                 otp.expires_at = now - timedelta(minutes=1)
#             otp.save()
#             return False, penalty_time, (otp.expires_at - now).total_seconds()
    
#     if action == 'resend':
#         now = timezone.now()
#         if not user:
#             return False
#         if not hasattr(user, 'otp'):
#             raise ValueError('This user has no otp')
        
#         otp = models.OTPChallenge.objects.select_for_update().get(user=user)
#         if now > max(otp.next_resend_at, otp.next_retry_at):
#             failed_attempts = otp.failed_attempts
#             new_failed_attempts = failed_attempts - (failed_attempts % settings.SECURITY_CODE_MAX_FAILED_ATTEMPTS)
#             code = generate_security_code(user)
#             otp.next_resend_at = now + timedelta(minutes=settings.SECURITY_CODE_RESEND_COOLDOWN_MINUTES)
#             otp.security_code = make_password(code)
#             otp.expires_at = now + timedelta(minutes=settings.SECURITY_CODE_EXPIRE_MINUTES)
#             otp.failed_attempts = new_failed_attempts + 1
#             otp.save()
#             send_security_code(code)
#             return True
#         else:
#             return False
    
#     if action == 'get_data':
#         now = timezone.now()
#         if not user:
#             return -1, -1, -1
#         otp = getattr(user, 'otp', None)
#         if otp:
#             next_retry = (otp.next_retry_at - now).total_seconds()
#             next_resend = (otp.next_resend_at - now).total_seconds()
#             expire = (otp.expires_at - now).total_seconds()
#         else:
#             next_retry = -1
#             next_resend = -1
#             expire = -1
#         return next_retry, next_resend, expire
#     raise ValueError(f'Action must be create or check or resend or get_data. Your action is {action}')


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

def normalize_phone_number(phone:str):
    if not phone:
        return False, phone
    # translation
    translation_table = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789',)
    phone_en = phone.translate(translation_table).replace(' ', '')

    if phone_en.startswith('0098'):
        phone_number = '+' + phone_en[2:]
    elif phone_en.startswith('98'):
        phone_number = '+' + phone_en
    elif phone_en.startswith('09'):
        phone_number = '+98' + phone_en[1:]
    else:
        phone_number = phone_en
    
    is_valid = phone_number[1:].isdigit() and len(phone_number) == 13 and phone_number.startswith('+98')
    return is_valid, phone_number


def consume_account_lookup_attempt(session):
    now = timezone.now()

    max_attempts = settings.ACCOUNT_REQUEST_MAX_ATTEMPTS
    window_hours = settings.ACCOUNT_REQUEST_WINDOW_HOURS

    request_count = session.get('request_count')
    window_started_at_str = session.get('window_started_at')

    if not request_count or not window_started_at_str:
        session['request_count'] = 1
        session['window_started_at'] = now.isoformat()
        return True

    try:
        window_started_at = datetime.fromisoformat(window_started_at_str)
    except (ValueError, TypeError):
        session['request_count'] = 1
        session['window_started_at'] = now.isoformat()
        return True


    if window_started_at < now - timedelta(hours=window_hours):
        session['request_count'] = 1
        session['window_started_at'] = now.isoformat()
        return True

    if request_count < max_attempts:
        session['request_count'] = request_count + 1
        return True

    return False