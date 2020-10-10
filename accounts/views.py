from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from .models import StudentProfile, TutorProfile, Countries
from tutoring.models import QuestionAnswer
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse
import json, re
from .seedDataInstaller import *

def login(request):
	if request.method == "POST":

		if cache.get('loginAttempts') != None and cache.get('loginAttempts') > 3:
			cache.set('loginAttempts', cache.get('loginAttempts'), 600)
			context = {"message": 'Your account has been temporarily locked out because of too many failed login attempts.'}
			return render(request,"accounts/login.html", context)

		username = request.POST['username'].replace(" ", "")
		password = request.POST['password']

		if not request.POST.get('remember_me', None):
			request.session.set_expiry(0)

		user = authenticate(username=username, password=password)
		if user:
			auth_login(request, user)
			return redirect('tutoring:mainpage')
		else:
			if cache.get('loginAttempts') == None:
				cache.set('loginAttempts', 1)
			else:
				cache.incr('loginAttempts', 1)

			context = {"message": "Username or Password did not match!", "username": username}
			return render(request,"accounts/login.html", context)
	return render(request,"accounts/login.html", {})

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
			return render(request,"accounts/registration.html", context)
		else:
			context = {}
			if(password!=password_2):
				context = {
					"message": "Your passwords do not match!",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,"accounts/registration.html", context)

			if(len(password)<8 or any(letter.isalpha() for letter in password)==False or any(capital.isupper() for capital in password)==False or any(number.isdigit() for number in password)==False):
				context = {
					"message": "Your password is not strong enough.",
					"email": email,
					"firstname": firstname,
					"lastname": lastname
				}
				return render(request,"accounts/registration.html", context)

			user = User.objects.create_user(username=email, email=email, password=password, first_name=firstname, last_name=lastname)
			user.is_active = False
			user.save()

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
			return render(request,"accounts/registration.html", context)
	return render(request,"accounts/registration.html", {})

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
		numberOfEducation = request.POST["numberOfEducation"]

		education = {}
		for i in range(int(numberOfEducation)):
			education["education_" + str(i + 1) ] = {"school_name": request.POST["school_name_" + str(i + 1)], "qualification": request.POST["qualification_" + str(i + 1)], "year": request.POST["year_" + str(i + 1)]}

		availability = {}
		availability["monday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["tuesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["wednesday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["thursday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["friday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["saturday"] = {"morning": False, "afternoon": False, "evening": False}
		availability["sunday"] = {"morning": False, "afternoon": False, "evening": False}

		TutorProfile.objects.create(user=request.user, userType="TUTOR", summary=summary, about=about, location=None, education=education, subjects=subjects, availability=availability, profilePicture=None)
		return redirect("accounts:createprofile")

	if request.method == "POST" and "student" in request.POST:
		# user is a student
		pass
	return render(request,"accounts/createprofile.html", {})



@login_required
def tutorprofile(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect("accounts:createprofile")
	
	tutorProfile.subjects = tutorProfile.subjects.split(",")
	countries = Countries.objects.all()

	questionAndAnswers = QuestionAnswer.objects.filter(answerer=tutorProfile.user)
	for i in questionAndAnswers:
		i.subject = i.subject.split(",")

	if request.method == "POST" and "updatePersonalDetails" in request.POST:
		firstname = request.POST["first_name"].strip()
		lastname = request.POST["last_name"].strip()

		user = User.objects.get(pk=(request.user.id))
		user.first_name = firstname
		user.last_name = lastname
		user.save()
		return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "message": "Your personal details has been updated successfully", "alert": "alert-success", "activeAccountTab": True})

	if request.method == "POST" and "updatePassword" in request.POST:
		currentPassword = request.POST["currentPassword"]
		newPassword = request.POST["newPassword"]
		confirmPassword = request.POST["confirmPassword"]

		user = User.objects.get(pk=(request.user.id))

		if currentPassword and not user.check_password(currentPassword):
			return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "message": "Your current password does not match", "alert": "alert-danger", "activeAccountTab": True})

		if(newPassword and confirmPassword):
			if(newPassword!=confirmPassword):
				return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "message": "Your new password and confirm password does not match", "alert": "alert-danger", "activeAccountTab": True})

			if(len(newPassword)<8 or any(letter.isalpha() for letter in newPassword)==False or any(capital.isupper() for capital in newPassword)==False or any(number.isdigit() for number in newPassword)==False):
				return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "message": "Your new password is not strong enough.", "alert": "alert-warning", "activeAccountTab": True})

			user.set_password(newPassword)
		user.save()

		if(newPassword and confirmPassword):
			user = authenticate(username=user.username, password=newPassword)
			if user:
				auth_login(request, user)
			else:
				return redirect("accounts:login")

	if request.method == "POST" and "updateAddress" in request.POST:
		address_1 = request.POST["address_1"].strip().title()
		address_2 = request.POST["address_2"].strip().title()
		city = request.POST["city"].strip().title()
		stateProvice = request.POST["stateProvice"].strip().title()
		postalZip = request.POST["postalZip"].strip().upper()
		country = Countries.objects.get(alpha=request.POST["country"])
		location = {"address_1": address_1, "address_2": address_2, "city": city, "stateProvice": stateProvice,
					"postalZip": postalZip, "country": {"alpha": country.alpha, "name": country.name}}
		TutorProfile.objects.filter(user=request.user.id).update(location=location)
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
		tutorProfile.subjects = tutorProfile.subjects.split(",")
		return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "message": "Your location has been updated successfully", "alert": "alert-success", "activeAccountTab": True})
	
	return render(request,"accounts/tutorprofile.html", {"tutorProfile": tutorProfile, "countries": countries, "questionAndAnswers": questionAndAnswers})

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
		
		numberOfEducation = request.POST["numberOfEducation"]
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
		for i in range(int(numberOfEducation)):
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

	return

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
				return render(request,"accounts/password_reset_form.html", context)

			if(len(password_1)<8 or any(letter.isalpha() for letter in password_1)==False or any(capital.isupper() for capital in password_1)==False or any(number.isdigit() for number in password_1)==False):
				context = {"message": "Your password is not strong enough."}
				return render(request,"accounts/password_reset_form.html", context)

			user.set_password(password_1)
			user.save()
			return redirect("accounts:login")

	if user is not None and generate_token.check_token(user, token):
		return render(request, "accounts/password_reset_form.html",{})
	else:
		return render(request, "accounts/activate_failed.html",status=401)
