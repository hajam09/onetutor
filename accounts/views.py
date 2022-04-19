from datetime import datetime
import os
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as signIn
from django.contrib.auth import logout as signOut
from django.contrib.auth import user_logged_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from accounts.forms import GetInTouchForm
from accounts.forms import UserSettingsPasswordUpdateForm
from accounts.forms import PasswordChangeForm
from accounts.forms import LoginForm
from accounts.forms import RegistrationForm
from accounts.models import ParentProfile
from accounts.models import StudentProfile
from accounts.models import TutorProfile
from accounts.utils import generate_token
from dashboard.models import UserLogin
from dashboard.models import UserSession
from onetutor.decorators.deprecated import deprecated
from onetutor.operations import databaseOperations
from onetutor.operations import emailOperations
from onetutor.operations import generalOperations
from tutoring.models import Availability
from tutoring.models import Component



def login(request):

	if not request.session.session_key:
		request.session.save()

	if request.method == "POST":
		uniqueVisitorId = request.session.session_key

		if cache.get(uniqueVisitorId) is not None and cache.get(uniqueVisitorId) > 3:
			cache.set(uniqueVisitorId, cache.get(uniqueVisitorId), 600)

			messages.error(
				request, 'Your account has been temporarily locked out because of too many failed login attempts.'
			)
			return redirect('accounts:login')

		form = LoginForm(request, request.POST)

		if form.is_valid():
			cache.delete(uniqueVisitorId)

			UserSession.objects.create(
				user=request.user,
				ipAddress=generalOperations.getClientInternetProtocolAddress(request),
				userAgent=request.META['HTTP_USER_AGENT'],
				sessionKey=uniqueVisitorId
			)

			UserLogin.objects.create(
				user=request.user
			)
			return redirect('tutoring:mainpage')

		if cache.get(uniqueVisitorId) is None:
			cache.set(uniqueVisitorId, 1)
		else:
			cache.incr(uniqueVisitorId, 1)

	else:
		form = LoginForm(request)

	context = {
		"form": form
	}
	return render(request, 'accounts/login.html', context)


def register(request):

	if request.method == "POST":
		form = RegistrationForm(request.POST)
		if form.is_valid():
			newUser = form.save()
			emailOperations.sendEmailToActivateAccount(request, newUser)

			messages.info(
				request, 'We\'ve sent you an activation link. Please check your email.'
			)
			return redirect('accounts:login')
	else:
		form = RegistrationForm()

	context = {
		"form": form
	}
	return render(request, 'accounts/registration.html', context)


def logout(request):
	latestUserLogin = UserLogin.objects.filter(user=request.user).latest('id')
	latestUserLogin.logoutTime = datetime.now()
	latestUserLogin.save()

	signOut(request)

	previousUrl = request.META.get('HTTP_REFERER')
	if previousUrl:
		return redirect(previousUrl)

	return redirect('accounts:login')


@login_required
def selectProfile(request):

	if generalOperations.tutorProfileExists(request.user):
		return redirect('accounts:profile-general-settings', profile='tutor')
	elif generalOperations.studentProfileExists(request.user):
		return redirect('accounts:profile-general-settings', profile='student')
	elif generalOperations.parentProfileExists(request.user):
		return redirect('accounts:profile-general-settings', profile='parent')

	return render(request, 'accounts/select_profile.html')


@login_required
def createStudentProfile(request):
	# TODO: Create a form and use formset to create multiple educations.

	if request.method == "POST":
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

		today = datetime.today().date()
		birthDate = datetime.strptime(request.POST['dateOfBirth'], '%Y-%m-%d').date()
		age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))

		if age < 18:
			parentCode = request.POST["parentIdentifier"] or None
			# TODO: optimize this section later on.
			# parentProfile = next((c for c in ParentProfile.objects.filter(code=parentCode)), None)
			try:
				parentProfile = ParentProfile.objects.get(code=parentCode)
			except ParentProfile.DoesNotExist:
				messages.error(
					request,
					'Invalid parent code. We did not find your parent, please check the code again.'
				)
				return redirect('accounts:create-student-profile')
			parent = parentProfile.user

		else:
			parent = None

		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')

		databaseOperations.createEducationInBulk(request, schoolNames, qualifications, startDates, endDates)

		StudentProfile.objects.create(
			user=request.user,
			about=about,
			subjects=subjects,
			dateOfBirth=birthDate,
			parent=parent,
		)
		return redirect('tutoring:mainpage')

	return render(request, "accounts/createStudentProfile.html")

@login_required
def createTutorProfile(request):
	# TODO: Create a form and user formset to create multiple educations.
	tutorFeatures = Component.objects.filter(componentGroup__code="TUTOR_FEATURE").exclude(internalKey__in=['Pro', 'DBS'])
	highestEducations = Component.objects.filter(componentGroup__code="EDUCATION_LEVEL")

	if request.method == "POST" and "createTutorProfile" in request.POST:
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
		chargeRate = round(float(request.POST['chargeRate']), 2)

		# Delete all previous education for this user and create new object(s).request.POST.getlist('features[]')
		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')

		databaseOperations.createEducationInBulk(request, schoolNames, qualifications, startDates, endDates)

		profile, created = TutorProfile.objects.update_or_create(
			user=request.user,
			defaults={
				'summary': summary,
				'about': about,
				'subjects': subjects,
				'chargeRate': chargeRate,
			}
		)

		profile.features.clear()
		profile.teachingLevels.clear()

		profile.features.add(*[ i for i in tutorFeatures for j in request.POST.getlist('features[]') if i.code==j ])
		profile.teachingLevels.add(*[ i for i in highestEducations for j in request.POST.getlist('teachingLevels[]') if i.code==j ])

		Availability.objects.get_or_create(
			user=request.user
		)
		return redirect('tutoring:mainpage')

	context = {
		'tutorFeatures': tutorFeatures,
		'highestEducations': highestEducations,
	}
	return render(request, "accounts/createTutorProfile.html", context)


@login_required
def createParentProfile(request):

	if request.method == "POST":
		today = datetime.today().date()
		birthDate = datetime.strptime(request.POST['dateOfBirth'], '%Y-%m-%d').date()
		age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))

		if age < 18:
			messages.warning(
				request,
				'You need to be at least 18 years to create an account.'
			)
			return redirect('accounts:create-parent-profile')

		ParentProfile.objects.create(
			user=request.user,
			dateOfBirth=birthDate,
		)
		return redirect('accounts:profile-general-settings', profile='parent')

	return render(request, "accounts/createParentProfile.html")


@login_required
def profileGeneralSettings(request, profile):
	profileKey = profile.lower()

	if profileKey != 'tutor' and profileKey != 'student' and profileKey != 'parent':
		raise Http404

	profile = generalOperations.getProfileForUser(request.user)

	if profile is None:
		return redirect('accounts:select-profile')

	if not profileKey.title() + 'Profile' == profile.__class__.__name__:
		raise Http404

	if request.method == "POST":
		firstname = request.POST["firstName"].strip()
		lastname = request.POST["lastName"].strip()

		if "profilePicture" in request.FILES:
			if profile.profilePicture and 'profile-picture/default-img/' not in profile.profilePicture.url:
				previousProfileImage = os.path.join(settings.MEDIA_ROOT, profile.profilePicture.name)
				if os.path.exists(previousProfileImage):
					os.remove(previousProfileImage)

			profile.profilePicture = request.FILES["profilePicture"]
			profile.save(update_fields=['profilePicture'])

		user = request.user
		user.first_name = firstname
		user.last_name = lastname
		user.save(update_fields=['first_name', 'last_name'])

		messages.success(
			request,
			'Your personal details has been updated successfully.'
		)

	context = {
		"profile": profile,
	}
	# TODO: More the template to more appropriate location
	return render(request, 'accounts/tutor/profileGeneralSettings.html', context)


@login_required
def tutorBiographySettings(request):
	try:
		profile = TutorProfile.objects.select_related('user__availability').prefetch_related('features', 'teachingLevels').get(user=request.user)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:select-profile')

	educationLevelComponent = Component.objects.filter(componentGroup__code="EDUCATION_LEVEL")
	tutorFeatureComponent = Component.objects.filter(componentGroup__code="TUTOR_FEATURE").exclude(internalKey__in=['Pro', 'DBS'])

	if request.method == 'POST':
		profile.summary = request.POST["summary"]
		profile.about = request.POST["about"]
		profile.subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
		profile.chargeRate = round(float(request.POST['chargeRate']), 2)

		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')
		databaseOperations.createEducationInBulk(request, schoolNames, qualifications, startDates, endDates)

		availabilityChoices = request.POST.getlist('availabilityChoices')
		request.user.availability.delete()
		availability = Availability.objects.create(user=request.user)
		for i in availabilityChoices:
			setattr(availability, i, True)
		availability.save()

		profile.features.clear()
		profile.teachingLevels.clear()

		profile.features.add(*[i for i in tutorFeatureComponent for j in request.POST.getlist('features') if i.code == j])
		profile.teachingLevels.add(*[i for i in educationLevelComponent for j in request.POST.getlist('teachingLevels') if i.code == j])

		profile.save()
		messages.success(
			request,
			'Your biography and other details has been updated successfully.'
		)
		return redirect('accounts:tutor-biography-settings')

	context = {
		'profile': profile,
		'educationLevelComponent': educationLevelComponent,
		'tutorFeatureComponent': tutorFeatureComponent,
	}
	return render(request, 'accounts/tutor/tutorBiographySettings.html', context)


@login_required
def profileSecuritySettings(request, profile):
	profile = profile.lower()

	if profile != 'tutor' and profile != 'student' and profile != 'parent':
		raise Http404

	if not generalOperations.userHasProfile(request.user):
		return redirect('accounts:select-profile')

	if request.method == "POST":
		form = UserSettingsPasswordUpdateForm(request, request.POST)

		if form.is_valid():
			form.updatePassword()
			isSuccess = form.reAuthenticate(signIn)

			if not isSuccess:
				return redirect("accounts:login")
	else:
		form = UserSettingsPasswordUpdateForm(request)

	context = {
		'form': form,
	}
	# TODO: More the template to more appropriate location
	return render(request, 'accounts/tutor/profileSecuritySettings.html', context)


@login_required
def tutorNotificationSettings(request):
	return render(request, 'accounts/tutor/tutorNotificationSettings.html')


@login_required
def profileAccountSettings(request, profile):
	profile = profile.lower()

	if profile != 'tutor' and profile != 'student' and profile != 'parent':
		raise Http404

	if request.method == "POST" and "deleteAccount" in request.POST:
		if request.POST["delete-code"] == request.session.session_key:
			request.user.delete()
			messages.success(
				request,
				'Account deleted successfully'
			)
			return redirect('tutoring:mainpage')

		messages.error(
			request,
			'Account delete code is incorrect, please try again later.'
		)
	# TODO: More the template to more appropriate location
	return render(request, 'accounts/tutor/profileAccountSettings.html')


def studentBiographySettings(request):
	pass

def studentNotificationSettings(request):
	pass


def rules(request, ruleType):

	if ruleType == "privacyPolicy":
		TEMPLATE = "accounts/privacyPolicy.html"
	elif ruleType == "termsAndConditions":
		TEMPLATE = "accounts/termsAndConditions.html"
	else:
		# TODO: create a custom 404 page and redirect it to there.
		pass

	return render(request, TEMPLATE)


def activateAccount(request, uidb64, token):

	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
		user = None

	if user is not None and generate_token.check_token(user, token):
		user.is_active = True
		user.save()

		messages.success(
			request,
			'Account activated successfully'
		)
		return redirect('accounts:login')

	return render(request, "accounts/activateFailed.html", status=HTTPStatus.UNAUTHORIZED)

def passwordRequest(request):

	if request.method == "POST":
		email = request.POST["email"]

		try:
			user = User.objects.get(username=email)
		except User.DoesNotExist:
			user = None

		if user is not None:
			emailOperations.sendEmailToChangePassword(request, user)

		messages.info(
			request, 'Check your email for a password change link.'
		)

	return render(request, "accounts/passwordRequest.html")

def passwordChange(request, uidb64, token):

	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (DjangoUnicodeDecodeError, ValueError, User.DoesNotExist):
		user = None

	if request.method == "POST" and user is not None and generate_token.check_token(user, token):
		form = PasswordChangeForm(request, user, request.POST)

		if form.is_valid():
			form.updatePassword()
			return redirect("accounts:login")

	context = {
		'form': PasswordChangeForm(),
	}

	TEMPLATE = 'passwordResetForm' if user is not None and generate_token.check_token(user, token) else 'activateFailed'
	return render(request, 'accounts/{}.html'.format(TEMPLATE), context)

def requestDeleteCode(request):

	if not request.is_ajax():
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

def requestCopyOfData(request):

	if not request.is_ajax():
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

def cookieConsent(request):

	if not request.is_ajax():
		response = {
			"statusCode": HTTPStatus.FORBIDDEN,
			"message": "Bad Request"
		}
		return JsonResponse(response)

	if not request.session.session_key:
		request.session.save()

	consentStage = request.GET.get('consentStage')

	if consentStage == "ASKED":
		askConsent = not (UserSession.objects.filter(sessionKey=request.session.session_key).exists() or request.user.is_authenticated)

	elif consentStage == "CONFIRMED":
		user = None if isinstance(request.user, AnonymousUser) else request.user
		UserSession.objects.create(
			user=user,
			ipAddress=generalOperations.getClientInternetProtocolAddress(request),
			userAgent=request.META['HTTP_USER_AGENT'],
			sessionKey=request.session.session_key
		)
		askConsent = False
	elif consentStage == "REJECTED":
		askConsent = False

	response = {
		"statusCode": HTTPStatus.OK,
		"askConsent": askConsent
	}
	return JsonResponse(response)


def getInTouch(request):

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