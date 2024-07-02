# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView

# router = DefaultRouter()
# router.register(r'users', UserViewSet)

urlpatterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
]
