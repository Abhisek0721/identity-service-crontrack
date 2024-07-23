# users/views.py
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from workspaces.models import Workspace, WorkspaceMember
from workspaces.serializers import CreateWorkspaceSerializer, WorkspaceMemberSerializer
from core.utils.api_response import api_response
from drf_yasg.utils import swagger_auto_schema
from core.utils.decode_jwt import decode_jwt_token

class CreateWorkspaceView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
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

        

class UpdateWorkspaceView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @swagger_auto_schema(
        request_body=CreateWorkspaceSerializer,
        responses={status.HTTP_200_OK: "Workspace successful response"},
        operation_description="Update a workspace."
    )
    def patch(self, request):
        data = request.data
        serializer = CreateWorkspaceSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.update()
            return api_response(data=data, message="Workspace created successfully", status=status.HTTP_201_CREATED)

