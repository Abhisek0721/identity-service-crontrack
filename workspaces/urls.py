# users/urls.py
from django.urls import path, include
from workspaces.views import CreateWorkspaceView


workspace_patterns = [
    path('create-workspace', CreateWorkspaceView.as_view(), name='create workspace'),
]

urlpatterns = [
    path('workspace/', include((workspace_patterns, 'workspace'), namespace='workspace')),
]