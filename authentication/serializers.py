# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import UserSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload
        token['full_name'] = user.full_name
        token['email'] = user.email
        token["google_id"] = user.google_id
        return token

# Example: Serializer for decoding JWT
class CustomTokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password',
                  'google_id', 'profile_picture', 'bio')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return UserSerializer(user).data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get(
                'request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid login credentials.")
        else:
            raise serializers.ValidationError(
                "Must include 'email' and 'password'.")

        # Custom token serializer to include additional fields
        token_serializer = CustomTokenObtainPairSerializer()
        refresh_token = token_serializer.get_token(user)
        return {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
            'user': UserSerializer(user).data,
        }
    

class ResendVerificationEmailDTO(serializers.Serializer):
    email = serializers.EmailField()

class VerifyUserDTO(serializers.Serializer):
    verification_token = serializers.UUIDField()