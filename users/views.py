# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from identity_service_creato.utils.api_response import api_response

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return api_response(data=data, message="User registered successfully.", status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user_data = UserSerializer(validated_data["user"]).data
            response_data = {
                "refresh_token": validated_data["refresh"],
                "access_token": validated_data["access"],
                "user": user_data
            }
            return api_response(data=response_data, message="Login successful.", status=status.HTTP_200_OK)
