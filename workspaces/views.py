# users/views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from workspaces.models import Workspace, WorkspaceMember
from workspaces.serializers import CreateWorkspaceSerializer, WorkspaceSerializer, WorkspaceMemberSerializer, InviteMemberSerializer
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from core.utils.decode_jwt import decode_jwt_token

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
            data["members"] = WorkspaceMemberSerializer(members, many=True).data
            return api_response(data=data, message="Workspace fetched successfully", status=status.HTTP_200_OK)
        except Workspace.DoesNotExist:
            return api_response(data=None, message="Workspace not found", status=status.HTTP_404_NOT_FOUND)

class InviteMembers(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    # Invite members to workspace
    def post(self, request):
        user_id = decode_jwt_token(request).get('user_id')
        data = request.data
        data['invited_by'] = user_id
        serializer = InviteMemberSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            is_user_admin = WorkspaceMember.objects.filter(
                user=user_id,
                role='admin'
            ).filter()
            if(not is_user_admin):
                return api_response(data=None, message="User is not an admin", status=status.HTTP_403_FORBIDDEN)
            