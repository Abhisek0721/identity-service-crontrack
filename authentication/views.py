# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from authentication.serializers import RegisterSerializer, LoginSerializer, ResendVerificationEmailDTO, VerifyUserDTO
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models.signals import post_save
from core.rabbitmq import publish_email_verification
import json
from core.utils.verification_token import generate_and_save_token, get_data_from_token

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
            response_data = serializer.save()
            send_email_data = {
                "full_name": response_data.get("full_name"),
                "email": response_data.get("email"),
                "verification_token": generate_and_save_token(response_data.get('email'), 'email_verification'),
            }
            publish_email_verification(json.dumps(send_email_data))
            return api_response(data=response_data, message="User registered successfully", status=status.HTTP_201_CREATED)
        


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


class ResendVerificationEmailView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = ResendVerificationEmailDTO(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user = User.objects.filter(
                email=validated_data.get('email')
            ).first()
            if not user:
                return api_response(message="User with this email is not registered.", status=status.HTTP_400_BAD_REQUEST)
            send_email_data = {
                "full_name": user.full_name,
                "email": user.email,
                "verification_token": generate_and_save_token(user.email, 'email_verification'),
            }
            publish_email_verification(json.dumps(send_email_data))
            return api_response(message="Sent email verification successfully.", status=status.HTTP_200_OK)
        
class VerifyUserView(APIView):
    permission_classes = (AllowAny, )

    def patch(self, request):
        serializer = VerifyUserDTO(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user = get_data_from_token(validated_data.get('verification_token'))
            if not user:
                return api_response(message="Invalid or Expired verification link.", status=status.HTTP_400_BAD_REQUEST)
            User.objects.filter(
                email=user.get('email')
            ).update(
                verified=True
            )
            return api_response(message="Verified successfully.", status=status.HTTP_200_OK)