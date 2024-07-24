# users/urls.py
from django.urls import path, include
from authentication.views import RegisterView, LoginView, ResendVerificationEmailView, VerifyUserView, ForgotPasswordView


user_patterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('resend-verification-email', ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('verify-user', VerifyUserView.as_view(), name="verify_user"),
    path('send-forgot-password-email', ForgotPasswordView.as_view(), name='send_forgot_password_email'),
    path('change-forgot-password', ForgotPasswordView.as_view(), name="change_forgot_password")
]

urlpatterns = [
    path('auth/', include((user_patterns, 'auth'), namespace='auth')),
]