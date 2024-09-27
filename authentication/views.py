# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from authentication.serializers import RegisterSerializer, LoginSerializer, ResendVerificationEmailDTO, VerifyUserDTO, ForgotPasswordDTO, CustomTokenObtainPairSerializer, GoogleOAuthCodeDTO
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.rabbitmq import publish_email_verification
import json
from core.utils.verification_token import generate_and_save_token, get_data_from_token
from django.contrib.auth.hashers import make_password
from workspaces.models import WorkspaceMember
from workspaces.serializers import WorkspaceMemberSerializer
from users.serializers import UserSerializer
from django.conf import settings
from urllib.parse import urlencode
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
import requests
from django.shortcuts import redirect

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
            status.HTTP_200_OK: openapi.Response("Login successful."),
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

# Google Login API
class GoogleLoginView(APIView):
    permission_classes = (AllowAny, )

    # Get Google Login Url
    def get(self, request, *args, **kwargs):
        # Construct the Google OAuth2 URL
        params = {
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,  # Your Google Client ID
            'redirect_uri': f'{settings.BASE_URL}{settings.GOOGLE_LOGIN_REDIRECT_ENDPOINT}',  # The redirect URI after login
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        google_auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
        # Redirect to Google OAuth2 login
        return api_response(data={"google_login_url": google_auth_url}, message="Redirecting to Google login.", status=status.HTTP_302_FOUND)
    
    # Get access_token from Google OAuth Code
    @swagger_auto_schema(
        request_body=GoogleOAuthCodeDTO,
        responses={
            status.HTTP_200_OK: openapi.Response("Google login successful"),
        },
        operation_description="Login with google OAuth code."
    )
    def post(self, request, *args, **kwargs):
        serializer = GoogleOAuthCodeDTO(data=request.data)
        payload = { 'code': None }
        if serializer.is_valid(raise_exception=True):
            payload = serializer.data
        # Exchange authorization code for access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': payload.get('code'),
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': f'{settings.BASE_URL}{settings.GOOGLE_LOGIN_REDIRECT_ENDPOINT}',
            'grant_type': 'authorization_code',
        }
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            return api_response(message="Failed to obtain access token", status=status.HTTP_400_BAD_REQUEST)

        access_token = token_json['access_token']

        # Use access token to authenticate the user via Google
        strategy = load_strategy(request)
        try:
            backend = load_backend(strategy, 'google-oauth2', redirect_uri=None)
            user = backend.do_auth(access_token)
        except (MissingBackend, AuthTokenError, AuthForbidden) as e:
            return api_response(message=f"Google authentication failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

        print(user, "user-data")
        if user and user.is_active:
            # Generate JWT tokens
            token_serializer = CustomTokenObtainPairSerializer()
            refresh_token = token_serializer.get_token(user)

            # Fetch workspace details for the user
            workspace_member = WorkspaceMember.objects.filter(user=user.id).order_by("-created_at")
            user_workspace = None
            if workspace_member:
                user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data

            response_data = {
                'access_token': str(refresh_token.access_token),
                'user': UserSerializer(user).data,
                'user_workspace': user_workspace
            }

            return api_response(data=response_data, message="Google login successful", status=status.HTTP_200_OK)
        
        return api_response(message="Failed to login via Google", status=status.HTTP_400_BAD_REQUEST)


# Redirect to frontend login page after successful google login
class GoogleOAuthCallbackView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        code = request.query_params.get('code')
        if not code:
            return api_response(message="Authorization code not provided", status=status.HTTP_400_BAD_REQUEST)
        return redirect(f'{settings.FRONTEND_BASE_URL}/login?googleOAuthCode={code}')


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
            # Custom token serializer to include additional fields
            token_serializer = CustomTokenObtainPairSerializer()
            refresh_token = token_serializer.get_token(user)
            workspace_member = WorkspaceMember.objects.filter(
                user=user.id
            ).all().order_by("-created_at")
            user_workspace = None
            if workspace_member:
                user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data
            response_data = {
                'access_token': str(refresh_token.access_token),
                'user': UserSerializer(user).data,
                "user_workspace": user_workspace,
                'verified': True
            }
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