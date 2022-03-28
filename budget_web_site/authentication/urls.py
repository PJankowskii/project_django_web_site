from .views import register_page, UsernameValidationView, EmailValidationView, VerificationView, \
    logout, reset_password_page, CompletePasswordReset, login_page, PasswordValidationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt, csrf_protect

urlpatterns = \
    [
        path('register', register_page, name="register"),
        path('login', login_page, name="login"),
        path('logout', logout, name="logout"),
        path('reset-password', reset_password_page, name="reset-password"),
        path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate-username"),
        path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate-email"),
        path('validate-password', csrf_exempt(PasswordValidationView.as_view()), name="validate-password"),
        path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
        path('set-new-password/<uidb64>/<token>', CompletePasswordReset.as_view(), name="reset-user-password"),
    ]
