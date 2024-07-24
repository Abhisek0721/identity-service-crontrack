import logging
import traceback
import threading
from django.core.management.base import BaseCommand
from core.rabbitmq import consume_email_verification, consume_workspace_invite
from authentication.send_email import process_email_verification
from workspaces.send_invite_email import process_workspace_invite

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Consume messages from RabbitMQ queue'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to consume messages from RabbitMQ...'))

        try:
            # Define threads for consuming messages
            email_thread = threading.Thread(target=self.consume_email_verification)
            invite_thread = threading.Thread(target=self.consume_workspace_invite)

            # Start the threads
            email_thread.start()
            invite_thread.start()

            # Join the threads to wait for their completion
            email_thread.join()
            invite_thread.join()

        except Exception as error:
            logger.error("An error occurred while consuming messages: %s", error)
            traceback.print_exc()
            raise error

    def consume_email_verification(self):
        try:
            consume_email_verification(process_email_verification)
            self.stdout.write(self.style.SUCCESS('Consuming email verification messages...'))
        except Exception as error:
            logger.error("Error in email verification consumer: %s", error)
            traceback.print_exc()

    def consume_workspace_invite(self):
        try:
            consume_workspace_invite(process_workspace_invite)
            self.stdout.write(self.style.SUCCESS('Consuming workspace invite messages...'))
        except Exception as error:
            logger.error("Error in workspace invite consumer: %s", error)
            traceback.print_exc()
