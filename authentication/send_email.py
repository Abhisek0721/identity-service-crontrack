# myapp/callback.py
import json
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def process_message(body):
    message = json.loads(body)
    user = message.get('user')
    email = user.get('email')
    if email:
        send_verification_email(email)


def send_verification_email(email):
    subject = 'Verify Your Email Address'
    html_message = render_to_string('verification_email.html', {
        'username': "Abhisekh Upadhaya",
        'verification_link': "http://localhost:3000",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending message to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


