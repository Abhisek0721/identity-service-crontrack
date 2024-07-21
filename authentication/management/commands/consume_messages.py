# myapp/management/commands/consume_messages.py
from django.core.management.base import BaseCommand
from core.rabbitmq import consume_messages
from authentication.send_email import process_message

class Command(BaseCommand):
    help = 'Consume messages from RabbitMQ queue'

    def handle(self, *args, **kwargs):
        consume_messages(process_message)
