from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.utils import generate_token


def sendEmailToActivateAccount(request, user: User):
    if settings.DEBUG or user.is_active:
        return

    currentSite = get_current_site(request)
    emailSubject = "Activate your OneTutor Account"
    fullName = user.get_full_name()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_token.make_token(user)

    message = """
        Hi {},
        \n
        Welcome to OneTutor, thank you for your joining our service.
        We have created an account for you to unlock more features.
        \n
        please click this link below to verify your account
        http://{}/accounts/activate/{}/{}
        \n
        Thanks,
        The OneTutor Team
    """.format(fullName, currentSite.domain, uid, token)

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return


def sendEmailToChangePassword(request, user: User):
    currentSite = get_current_site(request)
    emailSubject = "Request to change OneTutor Password"
    fullName = user.get_full_name()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generate_token.make_token(user)

    message = """
            Hi {},
            \n
            You have recently request to change your account password.
            Please click this link below to change your account password.
            \n
            http://{}/accounts/password_change/{}/{}
            \n
            Thanks,
            The OneTutor Team
        """.format(fullName, currentSite.domain, uid, token)

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return


def sendEmailForAccountDeletionCode(request, user: User):
    emailSubject = "Account deletion code"
    fullName = user.get_full_name()
    deleteCode = request.session.session_key

    message = """
                Hi {},
                \n
                Below is the code to delete your account permanently.
                Copy the code and paste it on our website.
                \n
                Your code is: {}
                \n
                Thanks,
                The OneTutor Team
            """.format(fullName, deleteCode)

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return
