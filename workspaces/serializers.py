from uuid import UUID
from rest_framework import serializers
from workspaces.models import Workspace, WorkspaceMember
from users.models import User

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = ('id', 'workspace', 'user', 'role',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class CreateWorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ('id', 'workspace_name', 'created_by',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        try:
            created_by = validated_data.get('created_by')
            workspace_name = validated_data.get('workspace_name')
            # Get User object from email
            check_member = WorkspaceMember.objects.filter(
                workspace__workspace_name=str(workspace_name),
                user=created_by
            ).exists()
            if(check_member):
                raise serializers.ValidationError(f"User is already a member in a workspace!")
            
            workspace = Workspace.objects.create(**validated_data)
            member = WorkspaceMember.objects.create(
                workspace=workspace,
                user=created_by
            )
            workspace = CreateWorkspaceSerializer(workspace).data
            workspace["member"] = WorkspaceMemberSerializer(member).data
            return workspace
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User does not exist.")
