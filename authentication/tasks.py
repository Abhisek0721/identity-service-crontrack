from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import logging
from core.celery import app
from core.stop_celery_worker import stop_celery_worker
from celery.utils.log import get_task_logger
from time import sleep

logger = logging.getLogger(__name__)

# @shared_task
# def send_verification_email_task(instance):
#     logger.info("Task started")
#     sleep(3)
#     # verification_link = os.getenv('FRONTEND_BASE_URL') + f"/verify-user/{instance.id}"
#     # logger.info(verification_link, "verification_link")
#     subject = 'Verify Your Email Address'
#     html_message = render_to_string('verification_email.html', {
#         'username': "Abhisekh Upadhaya",
#         'verification_link': "http://localhost:3000",
#         'app_name': "Creato"
#     })
#     plain_message = strip_tags(html_message)
#     from_email = 'abhisek0721@gmail.com'
#     to_email = 'abhisek0721@gmail.com'
#     send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
#     return instance



logger = get_task_logger(__name__)
@shared_task(name='first_assignment')
def my_first_task(duration):
    print("Running a task...")
    sleep(duration)
    return('first_assignment_done')
