# from accounts.seed_data_installer import *
from accounts.models import Countries
from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import TutorProfile
from accounts.models import UserSession
from accounts.utils import generate_token
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from http import HTTPStatus
from tutoring.models import QuestionAnswer
import accounts.seed_data_installer
import datetime
import json
import os
import random
import re
import requests
import string

def login(request):
	if request.method == "POST":

		if cache.get('loginAttempts') != None and cache.get('loginAttempts') > 3:
			cache.set('loginAttempts', cache.get('loginAttempts'), 600)
			context = {
				"message": 'Your account has been temporarily locked out because of too many failed login attempts.'
			}
			return render(request, 'accounts/login.html', context)

		username = request.POST['username'].replace(" ", "")
		password = request.POST['password']

		if not request.POST.get('remember_me', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			login_user = authenticate_user(request, user)
			if login_user != True:
				return login_user

			auth_login(request, user)
			add_user_session(request, request.POST['browser_type'])
			return redirect('tutoring:mainpage')

		if cache.get('loginAttempts') == None:
			cache.set('loginAttempts', 1)
		else:
			cache.incr('loginAttempts', 1)

		context = {
			"message": "Username or Password did not match!",
			"username": username
		}
		return render(request, 'accounts/login.html', context)
	return render(request, 'accounts/login.html', {})

def authenticate_user(request, user):
	response = requests.get("http://ip-api.com/json").json()
	try:
		this_session = UserSession.objects.get(ip_address=response['query'])
	except UserSession.DoesNotExist:
		return True

	if this_session.allowed:
		return True

	context = {
		"message": "This IP has been blocked by OneTutor for some reasons. If you think there has been some mistake, please appeal.",
		"username": user.username
	}
	return render(request,'accounts/login.html', context)

def add_user_session(request, browser_type):
	# add_user_session(request, request.POST['browser_type'])
	response = requests.get("http://ip-api.com/json").json()
	try:
		this_session = UserSession.objects.get(ip_address=response['query'])
		this_hour_now = datetime.datetime.now(tz=None)
		diff = this_hour_now - this_session.login_time.replace(tzinfo=None)
		if (diff.total_seconds()/3600 > 12):
			# with the same ip, the user has logged in 12hrs later.
			# TODO: update the user session with the new login_time and device type.
			pass
	except UserSession.DoesNotExist:
		user_agent = request.META['HTTP_USER_AGENT']
		platform = re.sub(r'\W+', '', user_agent.split()[1]) # Windows, Mac, Linux, Android, etc.
		device_type = "{}, {}".format(browser_type, platform)
		location="{}, {}, {}".format(response['city'], response['regionName'], response['country'])
		UserSession.objects.create(
			user=request.user,
			device_type=device_type,
			location=location,
			ip_address=response['query'],
		)

def register(request):
	if request.method == "POST":
		email = request.POST['email']
		password = request.POST['password']
		password_2 = request.POST['confirm_password'];
		firstname = request.POST['first_name']
		lastname = request.POST['last_name']		

		if User.objects.filter(username=email).exists():
			context = {
				"message": "An account already exists for this email address!",
				"email": email,
				"firstname": firstname,
				"lastname": lastname
			}
			return render(request,'accounts/registration.html', context)
		else:
			context = {}
			if(password!=password_2):
				context = {
					"message": "Your passwords do not match!",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,'accounts/registration.html', context)

			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				context = {
					"message": "Your password is not strong enough.",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,'accounts/registration.html', context)

			user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
			user.is_active = settings.DEBUG
			user.save()

			if not settings.DEBUG:
				# No need to send an email during debug.
				current_site = get_current_site(request)
				email_subject = "Activate your OneTutor Account"
				message = render_to_string('accounts/activate.html',
					{"user":user,
					"domain":current_site.domain,
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"token": generate_token.make_token(user)
					})

				email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
				email_message.send()

			context = {"activate": "We've sent you an activation link. Please check your email."}
			return render(request,'accounts/registration.html', context)
	return render(request,'accounts/registration.html', {})

def logout(request):
	auth_logout(request)
	return redirect('accounts:login')

@login_required
def createprofile(request):
	# only allowed for the user who do not have a profile yet
	if TutorProfile.objects.filter(user=request.user.id).exists() or StudentProfile.objects.filter(user=request.user.id).exists():
		return redirect('accounts:profile')

	if request.method == "POST" and "tutor" in request.POST:
		# user is a tutor
		summary = request.POST["summary"]
		about = request.POST["about"]
		subjects = request.POST["subjects"]

		education = {}
		for i in range(int( request.POST["numberOfEducation"])):
			education["education_" + str(i + 1) ] = {"school_name": request.POST["school_name_" + str(i + 1)], "qualification": request.POST["qualification_" + str(i + 1)], "year": request.POST["year_" + str(i + 1)]}

		availability = {}
		availability["monday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["tuesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["wednesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["thursday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["friday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["saturday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["sunday"] = {"morning": False, "afternoon": False, "evening": False}

		country = Countries.objects.get(alpha=request.POST["country"])
		location = {
			"address_1": request.POST["address_1"].strip().title(),
			"address_2": request.POST["address_2"].strip().title(),
			"city": request.POST["city"].strip().title(),
			"stateProvince": request.POST["stateProvince"].strip().title(),
			"postalZip": request.POST["postalZip"].strip().upper(),
			"country": {
				"alpha": country.alpha,
				"name": country.name
			}
		}

		TutorProfile.objects.create(user=request.user, summary=summary, about=about, location=location, education=education, subjects=subjects, availability=availability)
		return redirect('accounts:createprofile')

	if request.method == "POST" and "student" in request.POST:
		# user is a student
		pass
	countries = Countries.objects.all()
	return render(request,"accounts/createprofile.html", {"countries": countries})

@login_required
def tutorprofile(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:createprofile')
	
	tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")
	return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile})

@login_required
def user_settings(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect('accounts:createprofile')

	countries = Countries.objects.all()
	social_links = SocialConnection.objects.get(user=request.user) if SocialConnection.objects.filter(user=request.user).count() != 0 else None
	user_sessions = UserSession.objects.filter(user=request.user)

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
		delete_code = request.POST["delete-code"]
		if "user_" + str(request.user.id) + "_delete_key" in request.session and delete_code == request.session["user_" + str(request.user.id) + "_delete_key"]:
			u = User.objects.get(pk=request.user.id)
			u.delete()
			del request.session["user_" + str(request.user.id) + "_delete_key"]
			messages.add_message(request,messages.SUCCESS,"Account deleted successfully")
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

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "block_unblock_IP":
			session_id, allow = request.GET.get('session_id', None), request.GET.get('allow', None)
			allow = True if allow == 'true' else False
			this_session = UserSession.objects.get(id=session_id)
			this_session.allowed = allow
			this_session.save()
			if allow:
				message = "{} has been unblocked".format(this_session.ip_address)
			else:
				message = "{} has been blocked".format(this_session.ip_address)
			response = {
				"status_code": HTTPStatus.OK,
				"message": message
			}
			return HttpResponse(json.dumps(response), content_type="application/json")


	context = {
		"tutorProfile": tutorProfile,
		"countries": countries,
		"social_links": social_links,
		"user_sessions": user_sessions
	}
	
	return render(request, "accounts/user_settings.html",context)

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
		return redirect("accounts:profile")

	tutorProfile = TutorProfile.objects.get(user=request.user.id)
	return render(request,"accounts/tutorprofileedit.html", {"tutorProfile": tutorProfile})

@login_required
def studentprofile(request):
	return render(request,"accounts/studentprofile.html", {})

@login_required
def studentprofileedit(request):
	return render(request,"accounts/studentprofile.html", {})

@login_required
def profile(request):
	if not TutorProfile.objects.filter(user=request.user.id).exists() and not StudentProfile.objects.filter(user=request.user.id).exists():
		return redirect('accounts:createprofile')

	if TutorProfile.objects.filter(user=request.user.id).exists():
		return redirect("accounts:tutorprofile")

	if StudentProfile.objects.filter(user=request.user.id).exists():
		return render("accounts:studentprofile")

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
		messages.add_message(request,messages.SUCCESS,"Account activated successfully")
		return redirect('accounts:login')
	return render(request, "accounts/activate_failed.html",status=401)

def password_request(request):
	if request.method == "POST":
		email = request.POST["email"]

		try:
			user = User.objects.get(username=email)
		except User.DoesNotExist:
			user = None

		if user is not None:
			username = user.first_name

			current_site = get_current_site(request)
			domain = current_site.domain

			uid = urlsafe_base64_encode(force_bytes(user.pk))
			token = generate_token.make_token(user)

			email_subject = "Request to change OneTutor Password"
			message = """Hi {},\n\n
			You have recently request to change your account password.
			Please click this link below to change your account password. \n\n
			http://{}/accounts/password_change/{}/{}""".format(username, domain, uid, token)

			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
			email_message.send()

		return render(request, "accounts/password_request.html",{"message": "Check your email for a password change link."})
	return render(request, "accounts/password_request.html",{})

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

	# generate a random string, send it to the user's email and add it to the session.
	delete_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
	request.session["user_" + str(request.user.id) + "_delete_key"] = delete_code

	subject = 'Account deletion code.'
	message = """Hi {},\n\n Below is the code to delete your account permanently. Copy the code and paste it on our website. \n\n Your codeis: {}""".format(" ".join(request.user.first_name), delete_code)
	email_message = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [request.user.email])
	email_message.send()

	response = {
		"status_code": HTTPStatus.OK,
		"message": "Check your email for the code."
	}
	return HttpResponse(json.dumps(response), content_type="application/json")