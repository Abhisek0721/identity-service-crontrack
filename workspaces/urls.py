# users/urls.py
from django.urls import path, include
from workspaces.views import WorkspaceView


workspace_patterns = [
    path(r'', WorkspaceView.as_view(), name='create workspace'),
    path(r'', WorkspaceView.as_view(), name='update workspace'),
    path(r'<str:workspace_id>/', WorkspaceView.as_view(), name='get workspace')
]

urlpatterns = [
    path('workspace/', include((workspace_patterns, 'workspace'), namespace='workspace')),
]