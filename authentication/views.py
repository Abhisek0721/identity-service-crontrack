# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from authentication.serializers import RegisterSerializer, LoginSerializer
from identity_service_creato.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from users.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={status.HTTP_201_CREATED: "Successful signup response."},
        operation_description="Register a new user."
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return api_response(data=data, message="User registered successfully", status=status.HTTP_201_CREATED)
        


class LoginView(APIView):
    permission_classes = (AllowAny, )
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response("Successful login response"),
        },
        operation_description="Login with username and password."
    )

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            response_data = {
                "access_token": validated_data["access_token"],
                "user": validated_data["user"]
            }
            return api_response(data=response_data, message="Login successful.", status=status.HTTP_200_OK)


def send_verification_email(user, verification_link):
    subject = 'Verify Your Email Address'
    html_message = render_to_string('verification_email.html', {
        'username': user.username,
        'verification_link': verification_link,
    })
    plain_message = strip_tags(html_message)
    from_email = 'your_email@gmail.com'  # Replace with your email
    to_email = user.email

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)


@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    print("Send Verification Email Event Triggered")
    if created:
        print("created an user!")
        verification_link = os.getenv('FRONTEND_BASE_URL') + f"/verify-user/{instance.id}"
        print(verification_link, "verification_link")
        subject = 'Verify Your Email Address'
        html_message = render_to_string('verification_email.html', {
            'username': instance.full_name,
            'verification_link': verification_link,
            'app_name': os.getenv('APP_NAME')
        })
        plain_message = strip_tags(html_message)
        from_email = os.getenv('EMAIL_HOST_USER')
        to_email = instance.email

        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)