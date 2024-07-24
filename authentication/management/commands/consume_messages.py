# myapp/management/commands/consume_messages.py
from django.core.management.base import BaseCommand
from core.rabbitmq import consume_email_verification, consume_workspace_invite
from authentication.send_email import process_email_verification
from workspaces.send_invite_email import process_workspace_invite

class Command(BaseCommand):
    help = 'Consume messages from RabbitMQ queue'

    def handle(self, *args, **kwargs):
        consume_email_verification(process_email_verification)
        consume_workspace_invite(process_workspace_invite)
