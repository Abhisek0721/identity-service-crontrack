# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from workspaces.models import WorkspaceMember
from workspaces.serializers import WorkspaceMemberSerializer
from core.utils.api_response import api_response
from users.models import User
from users.serializers import UserSerializer, UpdateUserProfileDTO, ChangePasswordDTO
from core.utils.decode_jwt import decode_jwt_token
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class UserView(APIView):
    permission_classes = (IsAuthenticated,)

    # Get User Data
    def get(self, request, *args, **kwargs):
        user_id = decode_jwt_token(request).get('user_id')
        all_workspace = request.query_params.get('all_workspace')
        user = get_object_or_404(User, id=user_id)
        data = UserSerializer(user).data
        if (all_workspace and all_workspace == 'true'):
            user_workspace = None
            workspace_member = WorkspaceMember.objects.filter(
                user=user.id
            ).all().order_by("-created_at")
            if workspace_member:
                user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data
                data["user_workspace"] = user_workspace
        return api_response(data=data, message="User profile data", status=status.HTTP_200_OK)
    

    # Update User
    @swagger_auto_schema(
        request_body=UpdateUserProfileDTO,
        responses={status.HTTP_200_OK: "User profile updated"},
        operation_description="Update user profile."
    )
    # Update User Data
    def patch(self, request, *args, **kwargs):
        user_id = decode_jwt_token(request).get('user_id')
        payload = request.data
        serializer = UpdateUserProfileDTO(data=payload)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(id=user_id)
            # Update only if fields are provided in the payload
            if 'full_name' in serializer.validated_data:
                user.full_name = serializer.validated_data['full_name']
            if 'bio' in serializer.validated_data:
                user.bio = serializer.validated_data['bio']
            user.save()  # Save the updated user
        data = UserSerializer(user).data
        return api_response(data=data, message="User profile updated", status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    # Change User's Password
    @swagger_auto_schema(
        request_body=ChangePasswordDTO,
        responses={status.HTTP_200_OK: "Password updated successfully"},
        operation_description="Change user's password."
    )
    def patch(self, request, *args, **kwargs):
        user_id = decode_jwt_token(request).get('user_id')
        payload = request.data
        serializer = ChangePasswordDTO(data=payload)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.get(id=user_id)
            # Verify the current password
            if not user.check_password(serializer.validated_data["current_password"]):
                return api_response(message="Wrong current password", status=status.HTTP_400_BAD_REQUEST)
            user.password = make_password(serializer.validated_data.get('new_password'))
            user.save()  # Save the updated user
            return api_response(message="Password updated successfully", status=status.HTTP_200_OK)