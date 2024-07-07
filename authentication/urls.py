# users/urls.py
from django.urls import path, include
from authentication.views import RegisterView, LoginView


user_patterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
]

urlpatterns = [
    path('auth/', include((user_patterns, 'auth'), namespace='auth')),
]