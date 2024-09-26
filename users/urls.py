# users/urls.py
from django.urls import path, include
from users.views import UserView, ChangePasswordView


user_patterns = [
    path(r'', UserView.as_view(), name='get or update user data'),
    path(r'change-password/', ChangePasswordView.as_view(), name="update user's password"),
]

urlpatterns = [
    path('user/', include((user_patterns, 'user'), namespace='user')),
]
