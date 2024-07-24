# myapp/callback.py
import json
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def process_email_verification(body):
    message = json.loads(body)
    full_name = message.get('full_name')
    email = message.get('email')
    verification_token = message.get('verification_token')
    if email and verification_token:
        send_verification_email(full_name, email, verification_token)



def send_verification_email(full_name, email, verification_token):
    subject = 'Verify Your Email Address'
    html_message = render_to_string('verification_email.html', {
        'username': full_name,
        'verification_link': f"http://localhost:3000/verify-email/{verification_token}",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending message to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


def send_workspace_invite(email, verification_token):
    subject = 'You are invited to workspace'
    html_message = render_to_string('verification_email.html', {
        'verification_link': f"{settings.FRONTEND_BASE_URL}/verify/verify-user/{verification_token}",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending message to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)