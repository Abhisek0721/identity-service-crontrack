# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializers import UserSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'verified', 'google_id', 'profile_picture',
                  'bio', 'last_login_ip', 'role', 'is_active', 'is_staff', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims to the token payload
        token['full_name'] = user.full_name
        token['email'] = user.email
        token["role"] = user.role
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
        fields = ('email', 'full_name', 'password', 'role',
                  'google_id', 'profile_picture', 'bio')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        token_serializer = CustomTokenObtainPairSerializer()
        refresh_token = token_serializer.get_token(user)
        return {
            'refresh_token': str(refresh_token),
            'access_token': str(refresh_token.access_token),
            'user': UserSerializer(user).data,
        }


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
