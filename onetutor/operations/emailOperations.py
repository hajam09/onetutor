from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def sendEmailToActivateAccount(request, user: User):
    currentSite = get_current_site(request)
    emailSubject = 'Activate your OneTutor Account'

    fullName = user.get_full_name()
    base64 = urlsafe_base64_encode(force_bytes(user.pk))

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    token = passwordResetTokenGenerator.make_token(user)

    message = f'''
        Hi {fullName},
        \n
        Welcome to OneTutor, thank you for your joining our service.
        We have created an account for you to unlock more features.
        \n
        please click this link below to verify your account
        http://{currentSite.domain + reverse('accounts:activate-account-request-view', kwargs={'base64': base64, 'token': token})}
        \n
        Thanks,
        The OneTutor Team
    '''

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return


def sendEmailToResetPassword(request, user: User):
    currentSite = get_current_site(request)
    emailSubject = 'Request to reset OneTutor Password'

    fullName = user.get_full_name()
    base64 = urlsafe_base64_encode(force_bytes(user.pk))

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    token = passwordResetTokenGenerator.make_token(user)

    message = f'''
        Hi {fullName},
        \n
        You have recently request to reset your account password.
        Please click this link below to update your account password.
        \n
        http://{currentSite.domain + reverse('accounts:password-reset-confirm-view', kwargs={'base64': base64, 'token': token})}
        \n
        Thanks,
        The OneTutor Team
    '''

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return None
