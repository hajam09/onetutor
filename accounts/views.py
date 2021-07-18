import json
import os
import re
from http import HTTPStatus

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from accounts.forms import LoginForm
from accounts.forms import RegistrationForm
from accounts.models import Countries
from accounts.models import SocialConnection
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
	auth_logout(request)
	return redirect('accounts:login')

@login_required
def selectprofile(request):
	if TutorProfile.objects.filter(user=request.user.id).exists():
		return redirect("accounts:tutorprofile")

	if StudentProfile.objects.filter(user=request.user.id).exists():
		return render("accounts:studentprofile")

	return render(request, 'accounts/select_profile.html', {})

@login_required
def create_student_profile(request):
	return render(request,"accounts/create_student_profile.html", {})

@login_required
def create_tutor_profile(request):

	if request.method == "POST" and "createTutorProfile" in request.POST:
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

		education = {}
		for i in range(int( request.POST["numberOfEducation"])):
			education["education_" + str(i + 1)] = {
				"school_name": request.POST["school_name_" + str(i + 1)],
				"qualification": request.POST["qualification_" + str(i + 1)],
				"year": request.POST["year_" + str(i + 1)]
			}

		availability = {
			"monday": {"morning": False, "afternoon": False, "evening": False},
			"tuesday": {"morning": False, "afternoon": False, "evening": False},
			"wednesday": {"morning": False, "afternoon": False, "evening": False},
			"thursday": {"morning": False, "afternoon": False, "evening": False},
			"friday": {"morning": False, "afternoon": False, "evening": False},
			"saturday": {"morning": False, "afternoon": False, "evening": False},
			"sunday": {"morning": False, "afternoon": False, "evening": False}
		}

		TutorProfile.objects.create(
			user=request.user,
			summary=summary,
			about=about,
			location={},
			education=education,
			subjects=subjects,
			availability=availability
			)
		return redirect('accounts:tutorprofile')

	return render(request, "accounts/create_tutor_profile.html")

@login_required
def tutorprofile(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:selectprofile')

	tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")
	return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile})

@login_required
def tutorprofileedit(request):
	if request.method == "POST" and "updateTutorProfile" in request.POST:
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = request.POST["subjects"]
		subjects = subjects.strip()
		subjects = re.sub(' +', ' ', subjects)
		subjects = re.sub(' ,+', ',', subjects)
		subjects = subjects.replace(", ", ",")
		subjects = subjects.split(",")
		subjects.sort()
		subjects = ", ".join(subjects)

		availabilityChoices = request.POST.getlist('availabilityChoices')

		availability = {}
		availability["monday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["tuesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["wednesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["thursday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["friday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["saturday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["sunday"] = {"morning": False, "afternoon": False, "evening": False}

		for i in availabilityChoices:
			i = i.split("_")
			weekDay = i[0]
			dayTime = i[1]
			availability[weekDay][dayTime] = True

		education = {}
		for i in range(int(request.POST["numberOfEducation"])):
			education["education_" + str(i + 1) ] = {"school_name": request.POST["school_name_" + str(i + 1)], "qualification": request.POST["qualification_" + str(i + 1)], "year": request.POST["year_" + str(i + 1)]}

		TutorProfile.objects.filter(user=request.user.id).update(user=request.user, summary=summary, about=about, education=education, subjects=subjects, availability=availability, profilePicture=None)
		return redirect("accounts:tutorprofile")

	tutorProfile = TutorProfile.objects.get(user=request.user.id)
	return render(request,"accounts/tutorprofileedit.html", {"tutorProfile": tutorProfile})

@login_required
def studentprofile(request):
	return render(request,"accounts/studentprofile.html", {})

@login_required
def studentprofileedit(request):
	return render(request,"accounts/studentprofile.html", {})

@login_required
def user_settings(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:selectprofile')

	countries = Countries.objects.all()
	social_links = SocialConnection.objects.get(user=request.user) if SocialConnection.objects.filter(user=request.user).count() != 0 else None

	if request.method == "POST" and "update_general_information" in request.POST:
		firstname = request.POST["first_name"].strip()
		lastname = request.POST["last_name"].strip()

		if "my-file-selector" in request.FILES:
			if tutorProfile.profilePicture and 'profilepicture/defaultimg/' not in tutorProfile.profilePicture.url:
				previousProfileImage = os.path.join(settings.MEDIA_ROOT, tutorProfile.profilePicture.name)
				if os.path.exists(previousProfileImage):
					os.remove(previousProfileImage)

			profilePicture = request.FILES["my-file-selector"]
			tutorProfile.profilePicture = profilePicture
			tutorProfile.save(update_fields=['profilePicture'])

		user = User.objects.get(pk=(request.user.id))
		user.first_name = firstname
		user.last_name = lastname
		user.save()

		messages.add_message(request,messages.SUCCESS,"Your personal details has been updated successfully")
		return redirect('/accounts/user_settings/')

	if request.method == "POST" and "update_address" in request.POST:
		address_1 = request.POST["address_1"].strip().title()
		address_2 = request.POST["address_2"].strip().title()
		city = request.POST["city"].strip().title()
		stateProvince = request.POST["stateProvince"].strip().title()
		postalZip = request.POST["postalZip"].strip().upper()
		country = Countries.objects.get(alpha=request.POST["country"])

		location = {
			"address_1": address_1,
			"address_2": address_2,
			"city": city,
			"stateProvince": stateProvince,
			"postalZip": postalZip,
			"country": {"alpha": country.alpha, "name": country.name}

		}
		TutorProfile.objects.filter(user=request.user.id).update(location=location)
		messages.add_message(request,messages.SUCCESS,"Your location has been updated successfully")
		return redirect('/accounts/user_settings/')

	if request.method == "POST" and "delete_account" in request.POST:
		if request.POST["delete-code"] == request.session.session_key:
			u = User.objects.get(pk=request.user.id)
			u.delete()
			messages.success(
				request, 'Account deleted successfully'
			)
			return redirect('tutoring:mainpage')

	if request.method == "POST" and "update_password" in request.POST:
		currentPassword = request.POST["currentPassword"]
		newPassword = request.POST["newPassword"]
		confirmPassword = request.POST["confirmPassword"]

		user = User.objects.get(pk=(request.user.id))

		if currentPassword and not user.check_password(currentPassword):
			messages.add_message(request,messages.ERROR,"Your current password does not match")
			return redirect('/accounts/user_settings/')

		if(newPassword and confirmPassword):
			if(newPassword!=confirmPassword):
				messages.add_message(request,messages.ERROR,"Your new password and confirm password does not match")
				return redirect('/accounts/user_settings/')

			if(len(newPassword)<8 or any(letter.isalpha() for letter in newPassword)==False or any(capital.isupper() for capital in newPassword)==False or any(number.isdigit() for number in newPassword)==False):
				messages.add_message(request,messages.WARNING,"Your new password is not strong enough")
				return redirect('/accounts/user_settings/')

			user.set_password(newPassword)
		user.save()

		if(newPassword and confirmPassword):
			user = authenticate(username=user.username, password=newPassword)
			if user:
				messages.add_message(request,messages.SUCCESS,"Your password has been updated")
				auth_login(request, user)
			else:
				messages.add_message(request,messages.ERROR,"Error occured while trying to log you again.")
				return redirect("accounts:login")

	if request.method == "POST" and "notification_settings" in request.POST:
		login_attempt_notification = True if request.POST.get('login_attempt_notification') else False
		question_notification = True if request.POST.get('question_notification') else False
		answer_on_forum = True if request.POST.get('answer_on_forum') else False
		message_on_chat = True if request.POST.get('message_on_chat') else False
		# Need to create a Notifications table for each user and add it to event listner.

	if request.method == "POST" and "social_links" in request.POST:
		twitter = request.POST["twitter"]
		facebook = request.POST["facebook"]
		google = request.POST["google"]
		linkedin = request.POST["linkedin"]
		obj, created = SocialConnection.objects.update_or_create(
			user=request.user,
			defaults={'twitter': twitter, 'facebook': facebook, 'google': google, 'linkedin': linkedin},
		)
		messages.add_message(request,messages.SUCCESS,"Your social connection has been updated successfully")
		return redirect('/accounts/user_settings/')

	context = {
		"tutorProfile": tutorProfile,
		"countries": countries,
		"social_links": social_links,
	}

	return render(request, "accounts/user_settings.html",context)

def rules(request, rule_type):
	if rule_type == "privacy_policy":
		return render(request,"accounts/privacypolicy.html", {})
	if rule_type == "terms_and_conditions":
		return render(request,"accounts/termsandconditions.html", {})

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
		messages.add_message(
			request,
			messages.SUCCESS,
			"Account activated successfully"
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

		messages.success(
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
		password_1 = request.POST["password_1"]
		password_2 = request.POST["password_2"]

		if password_1 and password_2:
			if(password_1!=password_2):
				context = {"message": "Your passwords do not match!"}
				return render(request,'accounts/password_reset_form.html', context)

			if(len(password_1)<8 or any(letter.isalpha() for letter in password_1)==False or any(capital.isupper() for capital in password_1)==False or any(number.isdigit() for number in password_1)==False):
				context = {"message": "Your password is not strong enough."}
				return render(request,'accounts/password_reset_form.html', context)

			user.set_password(password_1)
			user.save()
			return redirect("accounts:login")

	if user is not None and generate_token.check_token(user, token):
		return render(request, 'accounts/password_reset_form.html',{})
	else:
		return render(request, "accounts/activate_failed.html",status=401)

def request_delete_code(request):
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to request a code."
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.session.session_key:
		request.session.save()

	emailOperations.sendEmailForAccountDeletionCode(request, request.user)

	response = {
		"status_code": HTTPStatus.OK,
		"message": "Check your email for the code."
	}
	return HttpResponse(json.dumps(response), content_type="application/json")