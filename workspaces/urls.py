# users/urls.py
from django.urls import path, include
from workspaces.views import WorkspaceView, InviteMembersView, VerifyInvitedMembers, GetAllWorkspaceView


workspace_patterns = [
    path(r'', WorkspaceView.as_view(), name='create workspace'),
    path(r'', WorkspaceView.as_view(), name='update workspace'),
    path(r'get-all-workspaces/', GetAllWorkspaceView.as_view(), name='get all workspaces'),
    path(r'<str:workspace_id>/', WorkspaceView.as_view(), name='get workspace'),
    path(r'invite-members', InviteMembersView.as_view(), name='invite members'),
    path(r'add-member-to-workspace', VerifyInvitedMembers.as_view(), name='add_member_to_workspace')
]

urlpatterns = [
    path('workspace/', include((workspace_patterns, 'workspace'), namespace='workspace')),
]