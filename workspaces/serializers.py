from rest_framework import serializers
from workspaces.models import Workspace, WorkspaceMember
from users.models import User
from workspaces.constants import ROLE_CHOICES
from users.serializers import UserSerializer

class WorkspaceSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = Workspace
        fields = ('id', 'workspace_name', 'created_by',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'workspace_name', 'created_by',
                    'created_at', 'updated_at')
        
class WorkspaceMemberSerializer(serializers.ModelSerializer):
    workspace = WorkspaceSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceMember
        fields = ('id', 'workspace', 'user', 'role',
                    'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user(self, obj):
        # Include user data only if 'include_user' is set to True in the context
        if self.context.get('include_user', False):
            return UserSerializer(obj.user).data
        return
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation['user'] is None:
            # Remove the 'user' field entirely if it's None
            representation.pop('user')
        return representation

class CreateWorkspaceSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
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
            workspace["members"] = WorkspaceMemberSerializer(member).data
            return workspace
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User does not exist.")
        
    def update(self, instance, validated_data):
        try:
            workspace_name = validated_data.get('workspace_name', instance.workspace_name)
            
            instance.workspace_name = workspace_name
            instance.save()

            members = WorkspaceMember.objects.filter(workspace=instance.id)
            workspace_data = CreateWorkspaceSerializer(instance).data
            workspace_data["members"] = WorkspaceMemberSerializer(members, many=True).data
            return workspace_data
        except Exception as error:
            print(error)
            raise serializers.ValidationError("An error occurred during workspace update.")


class MemberDTO(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=ROLE_CHOICES)

class InviteMemberDTO(serializers.Serializer):
    workspace_id = serializers.UUIDField()
    members_to_invite = MemberDTO(many=True)

class VerifyInvitedMembersDTO(serializers.Serializer):
    verification_token = serializers.UUIDField()