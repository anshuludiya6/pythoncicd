import os
import random
import string
import bcrypt
import jwt
from rest_framework.exceptions import AuthenticationFailed
from .models import OTP, Token, Users
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta, timezone
import pytz
import secrets
import jwt
from django.template.loader import render_to_string

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

default_from_email = settings.DEFAULT_FROM_EMAIL

def send_verification_email(user):
    token = generate_secure_token(user.user_id)
    email = user.email
    verification_link = f"http://122.168.125.73:8080//authentication/verify_email/{token}"

    email_subject = 'Email Verification'
    email_body = render_to_string('verifyEmail.html', {'user': user.name,'verification_link': verification_link})

    try:
        send_mail(
            email_subject,  
            '',
            default_from_email,  
            [user.email],
            html_message=email_body,
            fail_silently=False  
        )
        print("Email sent successfully")
    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')

        
def generate_secure_token(user_id):
    token = secrets.token_hex(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=48)
    
    token_record = Token(token=token, user_id=user_id, expires_at=expires_at)
    token_record.save()  
    return token

def is_token_valid(token):
    try:
        token_record = Token.objects.get(token=token)
    except Token.DoesNotExist:
        return False, "Invalid token"
    if not token_record:
        return False, "Invalid token"
    if  datetime.now(timezone.utc) > token_record.expires_at:
        return False, "Expired token"  
    if token_record.used:
        return False, "Used token"  
    return True, None  

def current_pst_to_utc(): 
    pst_zone = pytz.timezone('US/Pacific')
    utc_zone = pytz.timezone('UTC')
 
    current_pst_time = datetime.now(pst_zone)
 
    utc_time = current_pst_time.astimezone(utc_zone)
   
    return utc_time


def generate_jwt_token_login(user):
    expiration_time = current_pst_to_utc() + timedelta(hours=12)
    payload = {
        'user_id': user.user_id,
        'exp': expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def generate_jwt_token(user_id):
    expiration_time = current_pst_to_utc() + timedelta(hours=12)
    payload = {
        'user_id': user_id,
        'exp': expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def get_user_by_token(token):
    token_record = Token.objects.get(token=token)
    if not token_record:
        return None
    user = Users.objects.get(user_id=token_record.user_id)
    return user


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(user, otp):
    # token = generate_secure_token(user.user_id)
    print()
    email_subject = 'Your OTP Code'
    email_body = render_to_string('otp_email.html', {
        'user': user.name,
        'otp': otp,
    })

    try:
        send_mail(
            email_subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_body,
            fail_silently=False
        )
        print("email send successfully.")
    except Exception as e:
        print(f'password: {settings.EMAIL_HOST_PASSWORD}')
        print(f'Failed to send OTP. Error: {str(e)}')

def set_user_otp(user):
    otp = generate_otp()
    otp_expires_at =  datetime.now(timezone.utc) + timedelta(minutes=2)

    otp_record, created = OTP.objects.update_or_create(
        user_id=user,
        defaults={
            'otp': otp,
            'otp_expires_at': otp_expires_at,
            'updated_on': datetime.now(timezone.utc),
        }
    )
    return otp

def verify(user_id, otp_input,):
    try:
        otp_record = OTP.objects.get(user_id=user_id, otp=otp_input)
    except OTP.DoesNotExist:
        return False, 'Invalid OTP. Please try again.'

    if  datetime.now(timezone.utc) > otp_record.otp_expires_at:
        return False, 'OTP has expired. Please request a new OTP.'  


    return True, 'OTP verified successfully.'

def decode_jwt_token(token):
    token = token.replace("Bearer ", "").strip()
    try:
        decode_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decode_payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")

def update_user_password(token, new_password):
    user = get_user_by_token(token)
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    
    user.password = hashed_password.decode('utf-8')
    user.save()

def reset_password_token(token):
    token_record = Token.objects.get(token=token)
    token_record.used = True
    token_record.save()


def get_user_email(user_id):
    try:
        user = Users.objects.get(user_id=user_id)
        if user:
            return user.email
        else:
            raise Exception('User not found')
    except Users.DoesNotExist:
        raise Exception('User not found')
    except Exception as e:
        raise Exception(str(e))