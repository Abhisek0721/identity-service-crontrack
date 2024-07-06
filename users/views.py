# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from identity_service_creato.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={status.HTTP_201_CREATED: "User registered successfully"},
        operation_description="Register a new user."
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return api_response(data=data, message="Successful signup response.", status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = (AllowAny,)
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response("Successful login response"),
        },
        operation_description="Login with username and password."
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                validated_data = serializer.validated_data
                user_data = UserSerializer(validated_data["user"]).data
                response_data = {
                    "refresh_token": validated_data["refresh_token"],
                    "access_token": validated_data["access_token"],
                    "user": user_data
                }
                return api_response(data=response_data, message="Login successful.", status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e), e)
            return api_response(data=None, message="Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
