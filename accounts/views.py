import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as signIn
from django.contrib.auth import logout as signOut
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from accounts.forms import LoginForm
from accounts.forms import RegistrationForm
from accounts.models import Education
from accounts.models import StudentProfile
from accounts.models import TutorProfile
from accounts.utils import generate_token
from onetutor.operations import emailOperations


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
def selectprofile(request):
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

		availability = {
			"monday": {"morning": False, "afternoon": False, "evening": False},
			"tuesday": {"morning": False, "afternoon": False, "evening": False},
			"wednesday": {"morning": False, "afternoon": False, "evening": False},
			"thursday": {"morning": False, "afternoon": False, "evening": False},
			"friday": {"morning": False, "afternoon": False, "evening": False},
			"saturday": {"morning": False, "afternoon": False, "evening": False},
			"sunday": {"morning": False, "afternoon": False, "evening": False}
		}

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
			availability=availability
			)
		return redirect('accounts:tutorprofile')

	return render(request, "accounts/createTutorProfile.html")

@login_required
def tutorprofile(request):
	# TODO: consider removing this view.
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:selectprofile')

	tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")
	return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile})

@login_required
def tutorprofileedit(request):
	# TODO: consider removing this view.
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:selectprofile')

	if request.method == "POST" and "updateTutorProfile" in request.POST:
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
		availabilityChoices = request.POST.getlist('availabilityChoices')

		availability = {
			"monday": {"morning": False, "afternoon": False, "evening": False},
			"tuesday": {"morning": False, "afternoon": False, "evening": False},
			"wednesday": {"morning": False, "afternoon": False, "evening": False},
			"thursday": {"morning": False, "afternoon": False, "evening": False},
			"friday": {"morning": False, "afternoon": False, "evening": False},
			"saturday": {"morning": False, "afternoon": False, "evening": False},
			"sunday": {"morning": False, "afternoon": False, "evening": False}
		}

		for i in availabilityChoices:
			i = i.split("_")
			weekDay = i[0]
			dayTime = i[1]
			availability[weekDay][dayTime] = True

		education = {}
		for i in range(int(request.POST["numberOfEducation"])):
			education["education_" + str(i + 1)] = {
				"school_name": request.POST["school_name_" + str(i + 1)],
				"qualification": request.POST["qualification_" + str(i + 1)],
				"year": request.POST["year_" + str(i + 1)]
			}

		tutorProfile.summary = summary
		tutorProfile.about = about
		tutorProfile.education = education
		tutorProfile.subjects = subjects
		tutorProfile.availability = availability
		tutorProfile.save()
		return redirect("accounts:tutorprofile")

	context = {
		"tutorProfile": tutorProfile
	}
	return render(request, "accounts/tutorprofileedit.html", context)


@login_required
def userSettings(request):

	try:
		profile = TutorProfile.objects.get(user=request.user)
	except TutorProfile.DoesNotExist:
		profile = StudentProfile.objects.get(user=request.user)
	except StudentProfile.DoesNotExist:
		return redirect('accounts:selectprofile')

	if isinstance(profile, TutorProfile):
		# functions specific to tutors.
		templateName = "accounts/tutorSettings.html"

		if request.method == "POST" and "updateTutorProfile" in request.POST:
			summary = request.POST["summary"]
			about = request.POST["about"]
			subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
			availabilityChoices = request.POST.getlist('availabilityChoices')

			availability = {
				"monday": {"morning": False, "afternoon": False, "evening": False},
				"tuesday": {"morning": False, "afternoon": False, "evening": False},
				"wednesday": {"morning": False, "afternoon": False, "evening": False},
				"thursday": {"morning": False, "afternoon": False, "evening": False},
				"friday": {"morning": False, "afternoon": False, "evening": False},
				"saturday": {"morning": False, "afternoon": False, "evening": False},
				"sunday": {"morning": False, "afternoon": False, "evening": False}
			}

			for i in availabilityChoices:
				i = i.split("_")
				weekDay = i[0]
				dayTime = i[1]
				availability[weekDay][dayTime] = True

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

			profile.summary = summary
			profile.about = about
			profile.subjects = subjects
			profile.availability = availability
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

			education = {}
			for i in range(int(request.POST["numberOfEducation"])):
				education["education_" + str(i + 1)] = {
					"school_name": request.POST["school_name_" + str(i + 1)],
					"qualification": request.POST["qualification_" + str(i + 1)],
					"year": request.POST["year_" + str(i + 1)]
				}

			profile.about = about
			profile.education = education
			profile.subjects = subjects
			profile.save()

			messages.success(
				request,
				'Your biography and other details has been updated successfully.'
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

			if len(newPassword) < 8 or not any(letter.isalpha() for letter in newPassword) or not any(
					capital.isupper() for capital in newPassword) or not any(
					number.isdigit() for number in newPassword):
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

	return render(request, templateName)

def rules(request, rule_type):
	if rule_type == "privacy_policy":
		return render(request,"accounts/privacypolicy.html")
	if rule_type == "terms_and_conditions":
		return render(request,"accounts/termsandconditions.html")

def not_found_page(request, *args, **argv):
	return render(request,"accounts/404.html", {})

def activateaccount(request, uidb64, token):

	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None

	if user is not None and generate_token.check_token(user, token):
		user.is_active = True
		user.save()
		messages.success(
			request,
			'Account activated successfully'
		)
		return redirect('accounts:login')

	return render(request, "accounts/activate_failed.html", status=401)

def password_request(request):

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
		return redirect('accounts:password_request')
	return render(request, "accounts/password_request.html", {})

def password_change(request, uidb64, token):

	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
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
				return redirect("accounts:password_change", uidb64=uidb64, token=token)

			if len(newPassword) < 8 or not any(letter.isalpha() for letter in newPassword) or not any(
					capital.isupper() for capital in newPassword) or not any(
				number.isdigit() for number in newPassword):
				messages.warning(
					request,
					'Your new password is not strong enough.'
				)
				return redirect("accounts:password_change", uidb64=uidb64, token=token)

			user.set_password(newPassword)
			user.save()
			return redirect("accounts:login")

	if user is not None and generate_token.check_token(user, token):
		return render(request, 'accounts/password_reset_form.html')
	return render(request, "accounts/activate_failed.html", status=401)

def requestDeleteCode(request):

	if not request.is_ajax():
		response = {
			"statusCode": 403,
			"message": "Bad Request"
		}
		return JsonResponse(response)

	if not request.user.is_authenticated:
		response = {
			"statusCode": 401,
			"message": "Login to request a code."
		}
		return JsonResponse(response)

	if not request.session.session_key:
		request.session.save()

	emailOperations.sendEmailForAccountDeletionCode(request, request.user)

	response = {
		"statusCode": 200,
		"message": "Check your email for the code."
	}
	return JsonResponse(response)