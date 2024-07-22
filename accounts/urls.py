from django.urls import path

from accounts.views import (
    loginView,
    logoutView,
    registrationView,
    activateAccountRequestView,
    passwordResetRequestView,
    passwordResetConfirmView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', loginView, name='login-view'),
    path('logout/', logoutView, name='logout-view'),
    path('register/', registrationView, name='register-view'),
    path('activate-account/<base64>/<token>/', activateAccountRequestView, name='activate-account-request-view'),
    path('password-reset-request/', passwordResetRequestView, name='password-reset-request-view'),
    path('password-reset-confirm/<base64>/<token>', passwordResetConfirmView, name='password-reset-confirm-view'),
]
