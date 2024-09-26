# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from authentication.serializers import RegisterSerializer, LoginSerializer, ResendVerificationEmailDTO, VerifyUserDTO, ForgotPasswordDTO
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models.signals import post_save
from core.rabbitmq import publish_email_verification
import json
from core.utils.verification_token import generate_and_save_token, get_data_from_token
from django.contrib.auth.hashers import make_password
from workspaces.models import WorkspaceMember
from workspaces.serializers import WorkspaceMemberSerializer

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
                "verification_token": generate_and_save_token(email=response_data.get('email'), verification_type='email_verification'),
            }
            publish_email_verification(json.dumps(send_email_data))
            return api_response(data=response_data, message="User registered successfully. Please verify your email.", status=status.HTTP_201_CREATED)
        


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
            workspace_member = WorkspaceMember.objects.filter(
                user=validated_data["user"].get('id')
            ).all().order_by("-created_at")
            user_workspace = None
            if workspace_member:
                user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data
            response_data = {
                "access_token": validated_data["access_token"],
                "user": validated_data["user"],
                "user_workspace": user_workspace
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
            response_data = {
                "verified": False
            }
            if not user:
                return api_response(data=response_data, message="Invalid or Expired verification link.", status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=user.get('email')).first()
            if not user:
                return api_response(data=response_data, message="User not found.", status=status.HTTP_404_NOT_FOUND)
            user.verified = True
            user.save()
            response_data['verified'] = True
            return api_response(data=response_data, message="Verified successfully.", status=status.HTTP_200_OK)
        

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny, )

    # Send forgot password email
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
                "verification_token": generate_and_save_token(email=user.email, verification_type='forgot_password'),
            }
            publish_email_verification(json.dumps(send_email_data))
            return api_response(message="Sent forgot password email.", status=status.HTTP_200_OK)
        
    # Update forgot password
    def patch(self, request):
        serializer = ForgotPasswordDTO(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user = get_data_from_token(validated_data.get('verification_token'))
            if not user:
                return api_response(message="Invalid or Expired verification link.", status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(email=user.get('email')).first()
            if not user:
                return api_response(message="User not found.", status=status.HTTP_404_NOT_FOUND)
            user.password = make_password(validated_data.get('new_password'))
            user.save()
            return api_response(message="Password changed successfully.", status=status.HTTP_200_OK)