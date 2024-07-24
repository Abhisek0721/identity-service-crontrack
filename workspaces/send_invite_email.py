# myapp/callback.py
import json
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def process_workspace_invite(body):
    message = json.loads(body)
    email = message.get('email')
    role = message.get('role')
    workspace_name = message.get('workspace_name')
    invited_by = message.get('invited_by')
    verification_token = message.get('verification_token')
    if email and verification_token:
        send_workspace_invite(email, role, workspace_name, invited_by, verification_token)


def send_workspace_invite(email, role, workspace_name, invited_by, verification_token):
    subject = f'You are invited to {workspace_name}  workspace'
    html_message = render_to_string('workspace_invite.html', {
        'invited_by': invited_by,
        'role': role,
        'workspace_name': workspace_name,
        'verification_link': f"http://localhost:3000/workspace-invite/{verification_token}",
        'app_name': "Creato"
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = email
    print(f"sending invite email to {email}")
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)