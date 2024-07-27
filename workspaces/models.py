# users/models.py
import uuid
from django.db import models
from users.models import User
from .constants import ROLE_CHOICES

class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace_name = models.CharField(max_length=255, null=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_workspaces')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.workspace_name


class WorkspaceMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, null=True, related_name='workspace_team')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_team')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='admin')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.id