# users/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from workspaces.models import Workspace, WorkspaceMember
from workspaces.serializers import CreateWorkspaceSerializer, WorkspaceSerializer, WorkspaceMemberSerializer, InviteMemberDTO, VerifyInvitedMembersDTO
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from core.utils.decode_jwt import decode_jwt_token
from core.rabbitmq import publish_workspace_invite
from core.utils.verification_token import generate_and_save_token, get_data_from_token
import json
import traceback
from users.models import User
from django.shortcuts import get_object_or_404


class WorkspaceView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    # Create Workspace
    @swagger_auto_schema(
        request_body=CreateWorkspaceSerializer,
        responses={status.HTTP_201_CREATED: "Workspace successful response"},
        operation_description="Create a new workspace."
    )
    def post(self, request, *args, **kwargs):
        user_id = decode_jwt_token(request).get('user_id')
        data = request.data
        data['created_by'] = user_id
        serializer = CreateWorkspaceSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            workspace_member = WorkspaceMember.objects.filter(
                user=user_id
            ).all().order_by("-created_at")
            user_workspace = None
            if workspace_member:
                user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data
                data["user_workspace"] = user_workspace
            return api_response(data=data, message="Workspace created successfully", status=status.HTTP_201_CREATED)

    # Update Workspace
    @swagger_auto_schema(
        request_body=CreateWorkspaceSerializer,
        responses={status.HTTP_200_OK: "Workspace successful response"},
        operation_description="Update a workspace."
    )
    def patch(self, request, *args, **kwargs):
        try:
            workspace_id = request.data.get("workspace_id")
            instance = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return api_response(data=None, message="Workspace not found", status=status.HTTP_404_NOT_FOUND)

        serializer = CreateWorkspaceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            updated_instance = serializer.save()
            return api_response(data=updated_instance, message="Workspace updated successfully", status=status.HTTP_200_OK)

    # Get Workspace
    def get(self, request, *args, **kwargs):
        try:
            workspace_id = kwargs.get('workspace_id')
            if not workspace_id:
                return api_response(data=None, message="workspace_id is required", status=status.HTTP_400_BAD_REQUEST)
            instance = Workspace.objects.get(pk=workspace_id)
            data = WorkspaceSerializer(instance).data
            members = WorkspaceMember.objects.filter(workspace=instance.id)
            data["members"] = WorkspaceMemberSerializer(members, many=True, context={'include_user': True}).data
            return api_response(data=data, message="Workspace fetched successfully", status=status.HTTP_200_OK)
        except Workspace.DoesNotExist:
            return api_response(data=None, message="Workspace not found", status=status.HTTP_404_NOT_FOUND)

class GetAllWorkspaceView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    # Get all workspaces of a member
    def get(self, request):
        user_id = decode_jwt_token(request).get('user_id')
        workspace_member = WorkspaceMember.objects.filter(
            user=user_id
        ).all().order_by('-created_at')
        user_workspace = None
        if workspace_member:
            user_workspace = WorkspaceMemberSerializer(workspace_member, many=True).data
        return api_response(data=user_workspace, message="Workspace data of a user", status=status.HTTP_200_OK)

class InviteMembersView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    # Invite members to workspace
    def post(self, request):
        try:
            user = decode_jwt_token(request)
            user_id = user.get('user_id')
            data = request.data
            serializer = InviteMemberDTO(data=data)
            if serializer.is_valid(raise_exception=True):
                is_user_admin = WorkspaceMember.objects.filter(
                    user=user_id,
                    workspace=data.get('workspace_id'),
                    role='admin'
                ).select_related('workspace').first()
                if(not is_user_admin):
                    return api_response(data=None, message="User is not an admin", status=status.HTTP_403_FORBIDDEN)
                for invite_data in serializer.data.get("members_to_invite"):
                    invite_data["verification_token"] = generate_and_save_token(
                        invite_data.get('email'), 'workspace_invite', 
                        invite_data.get('role'), data.get('workspace_id')
                    )
                    invite_data["workspace_name"] = is_user_admin.workspace.workspace_name
                    invite_data["invited_by"] = user.get("full_name")
                    print(invite_data)
                    publish_workspace_invite(json.dumps(invite_data))
                return api_response(data=data, message="Invited to the workspace successfully", status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            traceback.print_exc()
            raise error


class VerifyInvitedMembers(generics.UpdateAPIView):
    permission_classes = (AllowAny, )

    # Verify invited members
    def patch(self, request):
        try:
            data = request.data
            serializer = VerifyInvitedMembersDTO(data=data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            user_data = get_data_from_token(validated_data.get('verification_token'), delete_token=False)
            if not user_data:
                return api_response(message="Invalid or Expired verification link.", status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(email=user_data.get('email')).first()
            if not user:
                return api_response(message="User is not registered yet", status=status.HTTP_400_BAD_REQUEST)
            # Delete token if user is registered user
            get_data_from_token(validated_data.get('verification_token'), delete_token=True)
            workspace = get_object_or_404(Workspace, id=user_data.get("workspace_id"))
            workspace_member, is_created = WorkspaceMember.objects.update_or_create(
                workspace=workspace,
                user=user,
                defaults={"role": user_data.get("role")}
            )

            workspace_member_data = WorkspaceMemberSerializer(workspace_member).data
            message = f"User is added to {workspace.workspace_name} workspace as a {user_data.get('role')}"
            workspace_member_data["is_new_member"] = is_created
            return api_response(data=workspace_member_data, message=message, status=status.HTTP_200_OK)
        except Exception as error:
            print(error)
            traceback.print_exc()
            raise error