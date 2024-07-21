import pika
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging


logger = logging.getLogger(__name__)


def send_verification_email_task(instance):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='email_verification_queue')

    html_message = render_to_string('verification_email.html', {
        'username': "Abhisekh Upadhaya",
        'verification_link': "http://localhost:3000",
        'app_name': "Creato"
    })
    logging.info("Sending Email Verification Message")
    channel.basic_publish(exchange='', routing_key='email_verification_queue', body=str(html_message))
    connection.close()



def send_verification_email(html_message):
    subject = 'Verify Your Email Address'
    plain_message = strip_tags(html_message)
    from_email = 'abhisek0721@gmail.com'
    to_email = 'abhisek0721@gmail.com'
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
