from rest_framework import serializers
from workspaces.models import Workspace, WorkspaceMember

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ('id', 'workspace_name', 'created_by',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = ('id', 'workspace', 'user', 'role',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')