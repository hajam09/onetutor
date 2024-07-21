from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
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
        http://{currentSite.domain + reverse('accounts:activate-account-view', kwargs={'base64': base64, 'token': token})}
        \n
        Thanks,
        The OneTutor Team
    '''

    emailMessage = EmailMessage(emailSubject, message, settings.EMAIL_HOST_USER, [user.email])
    emailMessage.send()
    return


def sendEmailToChangePassword(request, user: User):
    currentSite = get_current_site(request)
    emailSubject = 'Request to change OneTutor Password'

    fullName = user.get_full_name()
    base64 = urlsafe_base64_encode(force_bytes(user.pk))

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    token = passwordResetTokenGenerator.make_token(user)

    message = f'''
            Hi {fullName},
            \n
            You have recently request to change your account password.
            Please click this link below to change your account password.
            \n
            http://{currentSite.domain + reverse('accounts:password-change', kwargs={'base64': base64, 'token': token})}
            \n
            Thanks,
            The OneTutor Team
        '''

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


def sendTutorRequestedStoredData(user, data):
    emailSubject = "Your stored information at OneTutor"
    htmlTemplate = get_template("newsletters/tutorRequestedData.html").render({'data': data})

    emailMultiAlternatives = EmailMultiAlternatives(
        subject=emailSubject,
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )

    emailMultiAlternatives.attach_alternative(htmlTemplate, "text/html")
    emailMultiAlternatives.send()
    return
