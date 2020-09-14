from datetime import datetime
from http import HTTPStatus

from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.db.models import BooleanField
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import reverse
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView

from accounts.forms import GetInTouchForm
from accounts.forms import LoginForm
from accounts.forms import PasswordChangeForm
from accounts.forms import RegistrationForm
from accounts.forms import UserSettingsPasswordUpdateForm
from accounts.models import ParentProfile, Component
from accounts.models import StudentProfile
from accounts.models import TutorProfile
from onetutor.decorators.deprecated import deprecated
from onetutor.operations import databaseOperations
from onetutor.operations import emailOperations
from onetutor.operations import generalOperations
from onetutor.utils.exception.UnauthorizedException import UnauthorizedException
from tutoring.models import Availability


def loginView(request):
    if request.user.is_authenticated:
        return redirect('tutoring:index-view')

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

        form = LoginForm(request, request.POST)

        if form.is_valid():
            cache.delete(uniqueVisitorId)
            redirectUrl = request.GET.get('next')
            if redirectUrl:
                return redirect(redirectUrl)
            return redirect('tutoring:index-view')

        if cache.get(uniqueVisitorId) is None:
            cache.set(uniqueVisitorId, 1)
        else:
            cache.incr(uniqueVisitorId, 1)

    else:
        form = LoginForm(request)

    context = {
        'form': form
    }
    return render(request, 'accounts/loginView.html', context)


def logoutView(request):
    logout(request)

    previousUrl = request.META.get('HTTP_REFERER')
    if previousUrl:
        return redirect(previousUrl)

    return redirect('tutoring:index-view')


def registrationView(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            newUser = form.save()
            emailOperations.sendEmailToActivateAccount(request, newUser)

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


def rules(request, ruleType):
    if ruleType.casefold() == "privacy-policy":
        TEMPLATE = "accounts/privacyPolicy.html"
    elif ruleType.casefold() == "terms-and-conditions":
        TEMPLATE = "accounts/termsAndConditions.html"
    else:
        raise Http404

    return render(request, TEMPLATE)


def activateAccountView(request, base64, token):
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

    return render(request, 'accounts/activateFailed.html', status=HTTPStatus.UNAUTHORIZED)


def passwordResetRequestView(request):
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.POST['email'])
        except User.DoesNotExist:
            user = None

        if user is not None:
            emailOperations.sendEmailToChangePassword(request, user)

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

    if request.method == 'POST' and user is not None and verifyToken:
        form = PasswordChangeForm(request, user, request.POST)

        if form.is_valid():
            form.updatePassword()
            return redirect('accounts:login-view')

    context = {
        'form': PasswordChangeForm(),
    }

    TEMPLATE = 'passwordResetConfirmView' if user is not None and verifyToken else 'activateFailed'
    return render(request, 'accounts/{}.html'.format(TEMPLATE), context)


class CreateProfileViewApi(TemplateView):

    def __init__(self, **kwargs):
        super().__init__()
        self.today = datetime.today().date()

    def get_template_names(self):
        request = self.request
        profileType = request.GET.get("type") if request.GET.get("type") is None else request.GET.get("type").casefold()

        if profileType is None:
            templateName = "accounts/selectProfileTemplate.html"
        elif profileType == "tutor":
            templateName = "accounts/createTutorProfile.html"
        elif profileType == "parent":
            templateName = "accounts/createParentProfile.html"
        elif profileType == "student":
            templateName = "accounts/createStudentProfile.html"
        else:
            raise NotImplementedError

        return templateName

    def handleStudentProfile(self):
        birthDate = datetime.strptime(self.request.POST.get("dateOfBirth"), "%Y-%m-%d").date()
        age = self.today.year - birthDate.year - ((self.today.month, self.today.day) < (birthDate.month, birthDate.day))

        if age < 18:
            parentCode = self.request.POST.get("parentIdentifier")
            try:
                parentProfile = ParentProfile.objects.select_related("user").get(code=parentCode)
            except ParentProfile.DoesNotExist:
                messages.error(
                    self.request,
                    "Invalid parent code. We did not find your parent, please check the code again."
                )
                return
            parent = parentProfile.user

        else:
            parent = None

        StudentProfile.objects.create(
            user=self.request.user,
            about=self.request.POST.get("about"),
            subjects="&#44;".join(self.request.POST.getlist("subjects")),
            dateOfBirth=birthDate,
            parent=parent,
        )
        return

    def handleParentProfile(self):
        birthDate = datetime.strptime(self.request.POST.get("dateOfBirth"), "%Y-%m-%d").date()
        age = self.today.year - birthDate.year - ((self.today.month, self.today.day) < (birthDate.month, birthDate.day))

        if age < 18:
            messages.error(
                self.request,
                "You have to be aged 18 years or older, to open a parent account."
            )
            return

        ParentProfile.objects.create(user=self.request.user, dateOfBirth=birthDate)

    def handleTutorProfile(self):
        profile = TutorProfile.objects.create(
            user=self.request.user,
            summary=self.request.POST.get("summary"),
            about=self.request.POST.get("about"),
            price=self.request.POST.get("rate")
        )
        Availability.objects.get_or_create(user=self.request.user)
        databaseOperations.createEducationInBulk(
            self.request,
            self.request.POST.getlist("schoolName"),
            self.request.POST.getlist("qualification"),
            self.request.POST.getlist("startDate"),
            self.request.POST.getlist("endDate")
        )

        featureIds = Component.objects.filter(
            componentGroup__code="TUTOR_FEATURE", code__in=self.request.POST.getlist("features")
        ).values_list("id", flat=True)
        profile.features.add(*featureIds)

    def post(self, request, **kwargs):
        profileType = request.GET.get("type") if request.GET.get("type") is None else request.GET.get("type").casefold()

        if profileType == "student":
            self.handleStudentProfile()
        elif profileType == "parent":
            self.handleParentProfile()
        elif profileType == "tutor":
            self.handleTutorProfile()
        else:
            raise NotImplementedError

        storage = get_messages(request)
        if len(storage) > 0:
            return redirect(reverse("accounts:create-profile") + f"?type={profileType.lower()}")

        return redirect("tutoring:index-view")


class SettingsView(View):

    def getTemplate(self):
        tabQuery = self.request.GET.get("tab")
        tab = tabQuery if tabQuery is None else tabQuery.lower()

        templates = {
            "general": "generalSettings.html",
            "biography": "biographySettings.html",
            "security": "securitySettings.html",
            "notification": "notificationSettings.html",
            "account": "accountSettings.html",
            "my-children": "myChildrenSettings.html",
        }
        return "accounts/settings/" + templates[tab]

    def getForm(self, *args):
        profileQuery, tabQuery = self.request.GET.get("profile"), self.request.GET.get("tab")
        profile = profileQuery if profileQuery is None else profileQuery.casefold()
        tab = tabQuery if tabQuery is None else tabQuery.casefold()

        if profile == "tutor" and tab == "security":
            return UserSettingsPasswordUpdateForm(*args)
        elif profile == "student" and tab == "security":
            return UserSettingsPasswordUpdateForm(*args)
        elif profile == "parent" and tab == "security":
            return UserSettingsPasswordUpdateForm(*args)

    def get(self, request, *args, **kwargs):
        profile = generalOperations.getProfileForUser(request.user)
        context = {
            "form": self.getForm(request),
            "profile": profile,
        }
        return render(request, self.getTemplate(), context)

    def postValidFormFurtherActions(self, form):
        if not self.request.user.is_authenticated:
            raise UnauthorizedException
        if isinstance(form, UserSettingsPasswordUpdateForm):
            form.updatePassword()
            form.reAuthenticate(auth.login)

    def handleDeleteAccount(self):
        if self.request.POST.get("delete-code") == self.request.session.session_key:
            self.request.user.delete()
            messages.success(
                self.request,
                "Account deleted successfully."
            )
            return True
        messages.error(
            self.request,
            "Account delete code is incorrect, please try again later."
        )
        return False

    def handleGeneralSettings(self):
        if "picture" in self.request.FILES:
            profile = generalOperations.getProfileForUser(self.request.user)
            generalOperations.removeProfilePictureFromServer(profile)
            profile.picture = self.request.FILES.get("picture")
            profile.save(update_fields=["picture"])

        user = self.request.user
        user.first_name = self.request.POST.get("firstName").strip()
        user.last_name = self.request.POST.get("lastName").strip()
        user.save(update_fields=["first_name", "last_name"])

        messages.success(
            self.request,
            "Your personal details has been updated successfully."
        )

    def handleTutorBiography(self):
        profile = self.request.user.tutorProfile
        profile.summary = self.request.POST.get("summary")
        profile.about = self.request.POST.get("about")
        profile.price = self.request.POST.get("rate")

        databaseOperations.createEducationInBulk(
            self.request,
            self.request.POST.getlist("schoolName"),
            self.request.POST.getlist("qualification"),
            self.request.POST.getlist("startDate"),
            self.request.POST.getlist("endDate")
        )

        profile.features.clear()
        profile.features.add(*self.request.POST.getlist("features"))

        days = ["Morning", "Afternoon", "Evening"]
        availability = self.request.user.availability
        for attribute in availability._meta.get_fields():
            if any([i in attribute.attname for i in days]) and isinstance(attribute, BooleanField):
                setattr(
                    availability,
                    attribute.attname,
                    attribute.attname in self.request.POST.getlist("availabilityChoices")
                )

        profile.save()
        availability.save()

        messages.success(
            self.request,
            "Your biography and other details has been updated successfully."
        )

    def handleStudentBiography(self):
        profile = self.request.user.studentProfile
        profile.about = self.request.POST.get("about")
        profile.subjects = "&#44;".join(self.request.POST.getlist("subjects"))

        profile.save()
        messages.success(
            self.request,
            "Your biography and other details has been updated successfully."
        )

    def post(self, request, *args, **kwargs):
        tabQuery, profileQuery = self.request.GET.get("tab"), self.request.GET.get("profile")
        tab = tabQuery if tabQuery is None else tabQuery.lower()
        profile = profileQuery if profileQuery is None else profileQuery.lower()

        form = self.getForm(request, request.POST)

        if form is not None and form.is_valid():
            self.postValidFormFurtherActions(form)

        elif "deleteAccount" in request.POST:
            if self.handleDeleteAccount():
                return redirect("tutoring:index-view")

        elif "generalSettings" in request.POST:
            self.handleGeneralSettings()
            return redirect(reverse("accounts:settings-view") + f"?profile={profile}&tab=general")

        elif "tutorBiography" in request.POST and profile == "tutor" and tab == "biography":
            self.handleTutorBiography()
            return redirect(reverse("accounts:settings-view") + f"?profile={profile}&tab=biography")

        elif "studentBiography" in request.POST and profile == "student" and tab == "biography":
            self.handleStudentBiography()
            return redirect(reverse("accounts:settings-view") + f"?profile={profile}&tab=biography")

        context = {"form": form}
        return render(request, self.getTemplate(), context)


# ---------------------------------------------------------------------- #


@deprecated("Use RequestDeleteCodeApiEventVersion1Component")
def requestDeleteCode(request):
    if not request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        response = {
            "statusCode": HTTPStatus.FORBIDDEN,
            "message": "Bad Request"
        }
        return JsonResponse(response)

    if not request.user.is_authenticated:
        response = {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "message": "Login to request a code."
        }
        return JsonResponse(response)

    if not request.session.session_key:
        request.session.save()

    emailOperations.sendEmailForAccountDeletionCode(request, request.user)

    response = {
        "statusCode": HTTPStatus.OK,
        "message": "Check your email for the code."
    }
    return JsonResponse(response)


@deprecated("Use RequestCopyOfDataApiEventVersion1Component")
def requestCopyOfData(request):
    # TODO: Create a method to collect student and parent stored data and send it to the requested user.
    # TODO: Parent can request data for all their children.
    # TODO: Include all the fields from tutor profile.

    if not request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
        response = {
            "statusCode": HTTPStatus.FORBIDDEN,
            "message": "Bad Request"
        }
        return JsonResponse(response)

    if not request.user.is_authenticated:
        response = {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "message": "Login to request your data."
        }
        return JsonResponse(response)

    profile = generalOperations.getProfileForUser(request.user)

    if isinstance(profile, TutorProfile):
        requestedData = generalOperations.getTutorRequestedStoredData(request, request.user)
        emailOperations.sendTutorRequestedStoredData(request.user, requestedData)

    response = {
        "statusCode": HTTPStatus.OK,
        "message": "A copy is sent to your email."
    }
    return JsonResponse(response)


@deprecated("Use CookieConsentApiEventVersion1Component")
def cookieConsent(request):
    # use CookieConsentApiEventVersion1Component
    # if not request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":
    # 	response = {
    # 		"statusCode": HTTPStatus.FORBIDDEN,
    # 		"message": "Bad Request"
    # 	}
    # 	return JsonResponse(response)
    #
    # if not request.session.session_key:
    # 	request.session.save()
    #
    # consentStage = request.GET.get('consentStage')
    #
    # if consentStage == "ASKED":
    # 	askConsent = not (UserSession.objects.filter(sessionKey=request.session.session_key).exists() or request.user.is_authenticated)
    #
    # elif consentStage == "CONFIRMED":
    # 	user = None if isinstance(request.user, AnonymousUser) else request.user
    # 	UserSession.objects.create(
    # 		user=user,
    # 		ipAddress=generalOperations.getClientInternetProtocolAddress(request),
    # 		userAgent=request.META['HTTP_USER_AGENT'],
    # 		sessionKey=request.session.session_key
    # 	)
    # 	askConsent = False
    # elif consentStage == "REJECTED":
    # 	askConsent = False

    response = {
        "statusCode": HTTPStatus.OK,
        "askConsent": ""
    }
    return JsonResponse(response)


def getInTouch(request):
    # TODO: Fix the error when the user does not enter the domain ending.
    if request.method == "POST":
        form = GetInTouchForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request, 'Your message has been received, We will contact you soon.'
            )
            return redirect("accounts:get-in-touch")
    else:
        form = GetInTouchForm()

    context = {
        "form": form,
    }
    return render(request, 'footer/getInTouch.html', context)


def ourFeatures(request):
    return render(request, 'footer/ourFeatures.html')
