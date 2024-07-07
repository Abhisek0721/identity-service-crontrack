from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'verified', 'google_id', 'profile_picture',
                  'bio', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')