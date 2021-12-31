import os
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as signIn
from django.contrib.auth import logout as signOut
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from accounts.forms import GetInTouchForm
from accounts.forms import LoginForm
from accounts.forms import RegistrationForm
from accounts.models import Education
from accounts.models import StudentProfile
from accounts.models import TutorProfile
from accounts.utils import generate_token
from dashboard.models import UserSession
from onetutor.operations import emailOperations
from onetutor.operations import generalOperations
from tutoring.models import Availability


#TODO: Use Availability from the model rather than from TutorProfile

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
	signOut(request)

	previousUrl = request.META.get('HTTP_REFERER')
	if previousUrl:
		return redirect(previousUrl)

	return redirect('accounts:login')


@login_required
def selectProfile(request):
	if TutorProfile.objects.filter(user=request.user.id).exists():
		return redirect("accounts:tutorprofile")

	if StudentProfile.objects.filter(user=request.user.id).exists():
		return render("accounts:studentprofile")

	return render(request, 'accounts/select_profile.html')


@login_required
def createStudentProfile(request):

	if request.method == "POST" and "createStudentProfile" in request.POST:
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')

		if len(schoolNames) == len(qualifications) == len(startDates) == len(endDates):
			# Delete all previous education for this user and create new object(s).
			request.user.education.all().delete()
			Education.objects.bulk_create(
				[
					Education(
						user=request.user,
						schoolName=schoolName,
						qualification=qualification,
						startDate=startDate,
						endDate=endDate
					)
					for schoolName, qualification, startDate, endDate in zip(schoolNames, qualifications, startDates, endDates)
				]
			)

		StudentProfile.objects.create(
			user=request.user,
			about=about,
			subjects=subjects
		)
		return redirect('accounts:studentprofile')

	return render(request, "accounts/createStudentProfile.html")

@login_required
def createTutorProfile(request):

	if request.method == "POST" and "createTutorProfile" in request.POST:
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

		# Delete all previous education for this user and create new object(s).
		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')

		if len(schoolNames) == len(qualifications) == len(startDates) == len(endDates):
			request.user.education.all().delete()
			Education.objects.bulk_create(
				[
					Education(
						user=request.user,
						schoolName=schoolName,
						qualification=qualification,
						startDate=startDate,
						endDate=endDate
					)
					for schoolName, qualification, startDate, endDate in zip(schoolNames, qualifications, startDates, endDates)
				]
			)

		TutorProfile.objects.create(
			user=request.user,
			summary=summary,
			about=about,
			subjects=subjects,
			)

		Availability.objects.create(
			user=request.user
		)
		return redirect('tutoring:mainpage')

	return render(request, "accounts/createTutorProfile.html")


@login_required
def userSettings(request):

	# TODO: Find a good code design for the below try/catch.
	try:
		profile = TutorProfile.objects.select_related('user').get(user=request.user)
	except TutorProfile.DoesNotExist:
		profile = None

	if profile is None:
		try:
			profile = StudentProfile.objects.select_related('user').get(user=request.user)
		except StudentProfile.DoesNotExist:
			profile = None

	if profile is None:
		return redirect('accounts:select-profile')

	if isinstance(profile, TutorProfile):
		# functions specific to tutors.
		templateName = "accounts/tutorSettings.html"

		if request.method == "POST" and "updateTutorProfile" in request.POST:
			summary = request.POST["summary"]
			about = request.POST["about"]
			subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
			availabilityChoices = request.POST.getlist('availabilityChoices')

			request.user.availability.delete()
			availability = Availability.objects.create(user=request.user)
			for i in availabilityChoices:
				setattr(availability, i, True)
			availability.save()

			profile.summary = summary
			profile.about = about
			profile.subjects = subjects
			profile.save()

			messages.success(
				request,
				'Your biography and other details has been updated successfully.'
			)

	else:
		# functions specific to students .
		templateName = "accounts/studentSettings.html"

		if request.method == "POST" and "updateStudentProfile" in request.POST:
			about = request.POST["about"]
			subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

			profile.about = about
			profile.subjects = subjects
			profile.save()

			messages.success(
				request,
				'Your biography and other details has been updated successfully.'
			)

	if request.method == "POST" and "updateEducation" in request.POST:

		# Delete all previous education for this user and create new object(s).
		schoolNames = request.POST.getlist('schoolName')
		qualifications = request.POST.getlist('qualification')
		startDates = request.POST.getlist('startDate')
		endDates = request.POST.getlist('endDate')

		if len(schoolNames) == len(qualifications) == len(startDates) == len(endDates):
			request.user.education.all().delete()
			Education.objects.bulk_create(
				[
					Education(
						user=request.user,
						schoolName=schoolName,
						qualification=qualification,
						startDate=startDate,
						endDate=endDate
					)
					for schoolName, qualification, startDate, endDate in zip(schoolNames, qualifications, startDates, endDates)
				]
			)

	if request.method == "POST" and "updateGeneralInformation" in request.POST:
		firstname = request.POST["firstName"].strip()
		lastname = request.POST["lastName"].strip()

		if "profilePicture" in request.FILES:
			if profile.profilePicture and 'profilepicture/defaultimg/' not in profile.profilePicture.url:
				previousProfileImage = os.path.join(settings.MEDIA_ROOT, profile.profilePicture.name)
				if os.path.exists(previousProfileImage):
					os.remove(previousProfileImage)

			profilePicture = request.FILES["profilePicture"]
			profile.profilePicture = profilePicture
			profile.save(update_fields=['profilePicture'])

		user = request.user
		user.first_name = firstname
		user.last_name = lastname
		user.save()

		messages.success(
			request,
			'Your personal details has been updated successfully.'
		)

	if request.method == "POST" and "changePassword" in request.POST:
		currentPassword = request.POST["currentPassword"]
		newPassword = request.POST["newPassword"]
		confirmPassword = request.POST["confirmPassword"]

		user = request.user

		if currentPassword and not user.check_password(currentPassword):
			messages.error(
				request,
				'Your current password does not match with the account\'s existing password.'
			)

		if newPassword and confirmPassword:
			if newPassword != confirmPassword:
				messages.error(
					request,
					'Your new password and confirm password does not match.'
				)

			if not generalOperations.isPasswordStrong(newPassword):
				messages.warning(
					request,
					'Your new password is not strong enough.'
				)

			user.set_password(newPassword)
		user.save()

		if newPassword and confirmPassword:
			user = authenticate(username=user.username, password=newPassword)
			if user:
				messages.success(
					request,
					'Your password has been updated.'
				)
				signIn(request, user)
			else:
				messages.warning(
					request,
					'Something happened. Try to login to the system.'
				)
				return redirect("accounts:login")

	if request.method == "POST" and "notificationSettings" in request.POST:
		loginAttemptNotification = True if request.POST.get('loginAttemptNotification') else False
		questionAnswerNotification = True if request.POST.get('questionAnswerNotification') else False
		answerOnForum = True if request.POST.get('answerOnForum') else False
		messageOnChat = True if request.POST.get('messageOnChat') else False
		# TODO: Need to create a Notifications table for each user and add it to event listener.

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

	context = {
		"profile": profile
	}
	return render(request, templateName, context)

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
		newPassword = request.POST["newPassword"]
		confirmPassword = request.POST["confirmPassword"]

		if newPassword and confirmPassword:
			if newPassword != confirmPassword:
				messages.error(
					request,
					'Your new password and confirm password does not match.'
				)
				return redirect("accounts:password-change", uidb64=uidb64, token=token)

			if not generalOperations.isPasswordStrong(newPassword):
				messages.warning(
					request,
					'Your new password is not strong enough.'
				)
				return redirect("accounts:password-change", uidb64=uidb64, token=token)

			user.set_password(newPassword)
			user.save()
			return redirect("accounts:login")

	TEMPLATE = 'passwordResetForm' if user is not None and generate_token.check_token(user, token) else 'activateFailed'
	return render(request, 'accounts/{}.html'.format(TEMPLATE))

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

	try:
		profile = request.user.tutorProfile
	except TutorProfile.DoesNotExist:
		profile = request.user.studentProfile

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
		if UserSession.objects.filter(sessionKey=request.session.session_key).exists():
			askConsent = False
		else:
			askConsent = True

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
			return redirect("accounts:getInTouch")
	else:
		form = GetInTouchForm()

	context = {
		"form": form,
	}
	return render(request, 'accounts/getInTouch.html', context)
