from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 
            'verified', 'googleId', 'profile_picture', 'bio',
            'date_of_birth', 'last_login_ip', 'role'
        ]
