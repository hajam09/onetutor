from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode

from accounts.forms import (
    LoginForm,
    RegistrationForm,
    CustomSetPasswordForm
)
from onetutor.operations import emailOperations


def loginView(request):
    if request.user.is_authenticated:
        return redirect('core:index-view')

    if not request.session.session_key:
        request.session.save()

    if request.method == 'POST':
        uniqueVisitorId = request.session.session_key

        if cache.get(uniqueVisitorId) is not None and cache.get(uniqueVisitorId) > 3:
            cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)

            messages.error(
                request,
                'Your account has been temporarily locked out because of too many failed login attempts.'
            )
            return redirect('accounts:login-view')

        form = LoginForm(request=request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            cache.delete(uniqueVisitorId)
            redirectUrl = request.GET.get('next')
            if redirectUrl:
                return redirect(redirectUrl)
            return redirect('core:index-view')

        if cache.get(uniqueVisitorId) is None:
            cache.set(uniqueVisitorId, 1)
        else:
            cache.incr(uniqueVisitorId, 1)
    else:
        form = LoginForm(request=request)

    context = {
        'form': form
    }
    return render(request, 'accounts/loginView.html', context)


def logoutView(request):
    logout(request)

    previousUrl = request.META.get('HTTP_REFERER')
    if previousUrl:
        return redirect(previousUrl)

    return redirect('core:index-view')


def registrationView(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            emailOperations.sendEmailToActivateAccount(request, user)

            messages.info(
                request,
                'We\'ve sent you an activation link. Please check your email.'
            )
            return redirect('accounts:login-view')
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'accounts/registrationView.html', context)


def activateAccountRequestView(request, base64, token):
    try:
        uid = force_str(urlsafe_base64_decode(base64))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()

    if user is not None and passwordResetTokenGenerator.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            'Account activated successfully'
        )
        return redirect('accounts:login-view')
    return render(request, 'accounts/linkFailedTemplate.html', status=HTTPStatus.UNAUTHORIZED)


def passwordResetRequestView(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST.get('email'))
        except User.DoesNotExist:
            user = None

        if user is not None:
            emailOperations.sendEmailToResetPassword(request, user)

        messages.info(
            request,
            'Check your email for a password change link.'
        )
    return render(request, 'accounts/passwordResetRequestView.html')


def passwordResetConfirmView(request, base64, token):
    try:
        uid = force_str(urlsafe_base64_decode(base64))
        user = User.objects.get(pk=uid)
    except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
        user = None

    passwordResetTokenGenerator = PasswordResetTokenGenerator()
    verifyToken = passwordResetTokenGenerator.check_token(user, token)

    userAndTokenVerified = user is not None and verifyToken
    if request.method == 'POST' and userAndTokenVerified:
        form = CustomSetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()
            return redirect('accounts:login-view')
    else:
        form = CustomSetPasswordForm(user)

    context = {
        'form': form,
    }

    template = 'passwordResetConfirmView' if userAndTokenVerified else 'linkFailedTemplate'
    return render(request, 'accounts/{}.html'.format(template), context)
