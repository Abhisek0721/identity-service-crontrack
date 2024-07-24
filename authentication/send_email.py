# myapp/callback.py
import json
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.utils.verification_token import get_data_from_token


def process_email_verification(body):
    message = json.loads(body)
    full_name = message.get('full_name')
    email = message.get('email')
    verification_token = message.get('verification_token')
    data_from_token = get_data_from_token(token=verification_token, delete_token=False)
    if email and verification_token and data_from_token.get('type') == 'email_verification':
        send_verification_email(full_name, email, verification_token)
    else:
        send_forgot_password_email(full_name, email, verification_token)



def send_verification_email(full_name, email, verification_token):
    subject = 'Verify Your Email Address'
    html_message = render_to_string('verification_email.html', {
        'username': full_name,
        'verification_link': f"{settings.FRONTEND_BASE_URL}/verify/verify-email/{verification_token}",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending message to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


def send_forgot_password_email(full_name, email, verification_token):
    subject = 'Change forgot password'
    html_message = render_to_string('forgot_password.html', {
        'username': full_name,
        'verification_link': f"{settings.FRONTEND_BASE_URL}/verify/forgot-password/{verification_token}",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending message to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)