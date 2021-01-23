from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from accounts.models import TutorProfile, Countries, SocialConnection, UserSession
from tutoring.models import QuestionAnswer
from django.contrib.messages import get_messages
import requests, json
# coverage run --source=accounts manage.py test accounts
class TestViewsLogin(TestCase):

	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('accounts:login')
		self.user_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")

	def test_login_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/login.html")

	def test_login_login_attempts(self):
		"""
			Credentials are incorrect.
			User temporarily blocked from authenticating.
		"""
		context = {
			"username": "nonexistentialuser@gmail.com",
			"password": "qWeRtY1234",
			"browser_type": "Chrome"
		}
		for i in range(4):
			response = self.client.post(self.url, context)

		self.assertNotEqual(cache.get('loginAttempts'), None)
		self.assertEqual(response.status_code, 200)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your account has been temporarily locked out because of too many failed login attempts.")

	def test_login_remember_me(self):
		pass

	def test_login_authenticate_valid_user(self):
		"""
			Credentials are correct.
		"""
		context = {
			"username": "barry.allen@yahoo.com",
			"password": "RanDomPasWord56",
			"browser_type": "Chrome"
		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/')
		self.assertIn('_auth_user_id', self.client.session)
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user_1.pk)

	def test_login_authenticate_invalid_user(self):
		"""
			Credentials are incorrect.
		"""
		context = {
			"username": "nonexistentialuser@gmail.com",
			"password": "qWeRtY1234",
			"browser_type": "Chrome"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Username or Password did not match!")
		self.assertIn("username", response.context)
		self.assertEquals(response.context["username"], "nonexistentialuser@gmail.com")
		self.assertTemplateUsed(response, "accounts/login.html")

	def test_logout(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		self.url = reverse('accounts:logout')
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/login/')
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_login_ip_address_blocked(self):
		"""
			User's credentials are correct.
			Buts user has blocked this IP address from their UserSession.
		"""
		context = {
			"username": "barry.allen@yahoo.com",
			"password": "RanDomPasWord56",
			"browser_type": "Chrome"
		}
		self.api_response = requests.get("http://ip-api.com/json").json()
		self.user_session = UserSession.objects.create(
			user=User.objects.get(username=context["username"]),
			device_type="Chrome, Windows",
			location="Barking, England, United Kingdom",
			ip_address=self.api_response['query'],
			allowed=False
		)
		# self.test_login_authenticate_valid_user()
		response = self.client.post(self.url, context)
		self.assertEquals(response.context["message"], "This IP has been blocked by OneTutor for some reasons. If you think there has been some mistake, please appeal.")
		self.assertEquals(response.context["username"], "barry.allen@yahoo.com")
		self.assertTemplateUsed(response, "accounts/login.html")

class TestViewsRegister(TestCase):

	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def setUp(self):
		self.client = Client()
		self.url = reverse('accounts:register')
		self.user_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")

	def test_login_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/registration.html")

	def test_register_account_exists(self):
		"""
			Testing whether an account already exists with the specified email address.
		"""
		context = {
			"email": "barry.allen@yahoo.com",
			"password": "qWeRtY1234",
			"confirm_password": "qWeRtY1234",
			"first_name": "Henry",
			"last_name": "Allen" 
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "An account already exists for this email address!")
		self.assertIn("email", response.context)
		self.assertEquals(response.context["email"], "barry.allen@yahoo.com")
		self.assertIn("firstname", response.context)
		self.assertEquals(response.context["firstname"], "Henry")
		self.assertIn("lastname", response.context)
		self.assertEquals(response.context["lastname"], "Allen")
		self.assertTemplateUsed(response, "accounts/registration.html")

	def test_register_password_not_matching(self):
		"""
			Unique email address.
			Testing whether the password 1 and password 2 are matching.
		"""
		context = {
			"email": "oliver.queen@yahoo.com",
			"password": "Password123",
			"confirm_password": "Password321",
			"first_name": "Oliver",
			"last_name": "Queen" 
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your passwords do not match!")
		self.assertIn("email", response.context)
		self.assertEquals(response.context["email"], "oliver.queen@yahoo.com")
		self.assertIn("firstname", response.context)
		self.assertEquals(response.context["firstname"], "Oliver")
		self.assertIn("lastname", response.context)
		self.assertEquals(response.context["lastname"], "Queen")
		self.assertTemplateUsed(response, "accounts/registration.html")

	def test_register_password_not_strong(self):
		"""
			Unique email address.
			Matching passwords.
			Testing whether the password is strong or not.
		"""
		context = {
			"email": "oliver.queen@yahoo.com",
			"password": "123",
			"confirm_password": "123",
			"first_name": "Oliver",
			"last_name": "Queen" 
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your password is not strong enough.")
		self.assertIn("email", response.context)
		self.assertEquals(response.context["email"], "oliver.queen@yahoo.com")
		self.assertIn("firstname", response.context)
		self.assertEquals(response.context["firstname"], "Oliver")
		self.assertIn("lastname", response.context)
		self.assertEquals(response.context["lastname"], "Queen")
		self.assertTemplateUsed(response, "accounts/registration.html")

	def test_register_create_account(self):
		"""
			Unique email address.
			Matching passwords.
			Strong passwords.
			Testing whether we can create an account and an activation link is sent.
		"""
		context = {
			"email": "oliver.queen@yahoo.com",
			"password": "Password123",
			"confirm_password": "Password123",
			"first_name": "Oliver",
			"last_name": "Queen" 
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("activate", response.context)
		self.assertEquals(response.context["activate"], "We've sent you an activation link. Please check your email.")
		self.assertTrue(User.objects.filter(username="oliver.queen@yahoo.com").exists())

class TestViewsCreateProfile(TestCase):
	
	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def setUp(self):
		self.client = Client()
		self.url = reverse('accounts:createprofile')
		self.user_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		Countries.objects.create(alpha='GB', name='United Kingdom')

	def test_createprofile_GET(self):
		"""
			User must be authenticated prior to calling the view.
		"""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/createprofile.html")

	def test_createprofile_create_tutor_profile(self):
		"""
			User must be authenticated prior to calling the view.
		"""
		context = {
			"tutor": "aa",
			"summary": "Summary for this particular tutor.",
			"about": "Short about section for this tutor.",
			"subjects": "English, Maths, Science, ICT",
			"numberOfEducation": "1" ,
			"school_name_1": "ECS",
			"qualification_1": "A-Levels",
			"year_1": "2010-2015",
			"country": "GB",
			"address_1": "99 Some Road",
			"address_2": "becontree",
			"city": "Cambridge",
			"stateProvice": "Sussex",
			"postalZip": "MU8 3SW",
		}
		count_before = TutorProfile.objects.all().count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertEqual(TutorProfile.objects.all().count(), count_before + 1)
		self.assertEqual(TutorProfile.objects.all().order_by('-id')[0].user, self.user_1)


	def test_createprofile_create_student_profile(self):
		pass

	def test_createprofile_tutor_profile_exists(self):
		"""
			User must be authenticated prior to calling the view.
		"""
		self.test_createprofile_create_tutor_profile()
		response = self.client.post(self.url, {})
		self.assertEquals(response.status_code, 302)

	def test_createprofile_student_profile_exists(self):
		pass

class TestViewsTutorProfile(TestCase):

	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def create_tutor_profile(self, u, s, a, su):
		location = {
						"address_1": "24 Cranborne Road",
						"address_2": "Barking",
						"city": "London",
						"stateProvice": "Essex", 
						"postalZip": "IG11 7XE",
						"country": { "alpha": "GB", "name": "United Kingdom" }
					}
		education = {
			"education_1": { "school_name": "Imperial College London", "qualification": "Computing (Masters) - 2:1", "year": "2016 - 2020" },
			"education_2": { "school_name": "Peter Symonds College", "qualification": "A Levels - A*A*AA (Maths, Computing, Further Maths, Physics)", "year": "2014 - 2016" },
			"education_3": { "school_name": "Perins School", "qualification": "GCSE - 10 x A* ", "year": "2009 - 2014" }
		}

		availability = {
			"monday": {"morning": True, "afternoon": False, "evening": False},
			"tuesday": {"morning": False, "afternoon": True, "evening": False},
			"wednesday": {"morning": False, "afternoon": False, "evening": False},
			"thursday": {"morning": False, "afternoon": True, "evening": False},
			"friday": {"morning": True, "afternoon": False, "evening": False},
			"saturday": {"morning": False, "afternoon": True, "evening": False},
			"sunday": {"morning": True, "afternoon": False, "evening": False}
		}
		
		return TutorProfile.objects.create(
			user=u,
			summary=s, about=a, location=location,
			education=education, subjects=su,
			availability=availability, profilePicture=None
		)

	def setUp(self):
		self.client = Client()
		self.url = reverse('accounts:tutorprofile')
		self.user_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')

	def test_tutorprofile_GET(self):
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")

	def test_tutorprofile_tutor_profile_does_not_exist(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does not exist to the authenticated user.
		"""
		response = self.client.post(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/createprofile/')
		self.assertIn('_auth_user_id', self.client.session)

class TestViewsUserSettings(TestCase):

	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def create_tutor_profile(self, u, s, a, su):
		location = {
						"address_1": "24 Cranborne Road",
						"address_2": "Barking",
						"city": "London",
						"stateProvice": "Essex", 
						"postalZip": "IG11 7XE",
						"country": { "alpha": "GB", "name": "United Kingdom" }
					}
		education = {
			"education_1": { "school_name": "Imperial College London", "qualification": "Computing (Masters) - 2:1", "year": "2016 - 2020" },
			"education_2": { "school_name": "Peter Symonds College", "qualification": "A Levels - A*A*AA (Maths, Computing, Further Maths, Physics)", "year": "2014 - 2016" },
			"education_3": { "school_name": "Perins School", "qualification": "GCSE - 10 x A* ", "year": "2009 - 2014" }
		}

		availability = {
			"monday": {"morning": True, "afternoon": False, "evening": False},
			"tuesday": {"morning": False, "afternoon": True, "evening": False},
			"wednesday": {"morning": False, "afternoon": False, "evening": False},
			"thursday": {"morning": False, "afternoon": True, "evening": False},
			"friday": {"morning": True, "afternoon": False, "evening": False},
			"saturday": {"morning": False, "afternoon": True, "evening": False},
			"sunday": {"morning": True, "afternoon": False, "evening": False}
		}
		
		return TutorProfile.objects.create(
			user=u,
			summary=s, about=a, location=location,
			education=education, subjects=su,
			availability=availability, profilePicture=None
		)

	def setUp(self):
		self.client = Client()
		self.url = reverse('accounts:user_settings')
		self.user_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		self.country = Countries.objects.create(alpha='GB', name='United Kingdom')

	def test_tutorprofile_GET(self):
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/user_settings.html")

	def test_tutorprofile_tutor_profile_does_not_exist(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does not exist to the authenticated user.
		"""
		response = self.client.post(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/createprofile/')
		self.assertIn('_auth_user_id', self.client.session)

	def test_tutorprofile_tutor_update_general_information(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User trying to update their first name, last name and photos
		"""

		context = {
			"first_name": "Cisco",
			"last_name": "Ramone",
			"update_general_information": ""
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		user = User.objects.get(username="barry.allen@yahoo.com")
		self.assertEqual(user.first_name, context["first_name"])
		self.assertEqual(user.last_name, context["last_name"])
		self.assertEqual(response.status_code, 302)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your personal details has been updated successfully')
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_tutorprofile_tutor_update_address(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User trying to update their address from their settings
		"""

		context = {
			"update_address": "",
			"address_1": "204 Eversholt Road",
			"address_2": "Euston",
			"city": "London",
			"stateProvice": "Essex",
			"postalZip": "YM5 2DG",
			"country": "GB"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		tutor_profile = TutorProfile.objects.get(user=self.user_1)
		new_location = {
			"address_1": context["address_1"],
			"address_2": context["address_2"],
			"city": context["city"],
			"stateProvice": context["stateProvice"],
			"postalZip": context["postalZip"],
			"country": {"alpha": self.country.alpha, "name": self.country.name}
		}
		self.assertEqual(tutor_profile.location, new_location)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your location has been updated successfully')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_tutorprofile_tutor_delete_account(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User trying to delete their account by entering the delete code.
		"""

		context = {
			"delete_account": "",
			"delete-code": "N4nfKJGjkfb"
		}

		session = self.client.session
		session["user_" + str(self.user_1.id) + "_delete_key"] = context["delete-code"]
		session.save()

		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEqual(User.objects.filter(email="barry.allen@yahoo.com").count(), 0)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Account deleted successfully')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/')

	def test_tutorprofile_tutor_update_password_mismatch_password(self):
		"""
			User must be authenticated prior to calling the view.
			User trying to update their password.
			Users current password does not match with existing password.
		"""

		context = {
			"update_password": "",
			"currentPassword": "MisMatchPassword",
			"newPassword": "u9EzQfgkgn6K",
			"confirmPassword": "u9EzQfgkgn6K"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your current password does not match')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_tutorprofile_tutor_update_password_newpassword_confirmpassowrd_unmatched(self):
		"""
			User must be authenticated prior to calling the view.
			User trying to update their password.
			Users new password and confirm password is unmatched
		"""
		context = {
			"update_password": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "u9EzQfgkgn6K",
			"confirmPassword": "r34tgg43gt"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your new password and confirm password does not match')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_tutorprofile_tutor_update_password_weak_password(self):
		"""
			User must be authenticated prior to calling the view.
			User trying to update their password.
			Users new password is not strong enough.
		"""
		context = {
			"update_password": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "123",
			"confirmPassword": "123"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your new password is not strong enough')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_tutorprofile_tutor_update_password_success(self):
		"""
			User must be authenticated prior to calling the view.
			User trying to update their password.
			Users new password passes all checklist.
		"""
		context = {
			"update_password": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "u9EzQfgkgn6K",
			"confirmPassword": "u9EzQfgkgn6K"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your password has been updated')
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "accounts/user_settings.html")

	def test_tutorprofile_tutor_add_update_social_links(self):
		"""
			User must be authenticated prior to calling the view.
			User is adding a new or updating their existing social links.
		"""
		context = {
			"social_links": "",
			"twitter": "twitterlink",
			"facebook": "facebooklink",
			"google": "googlelink",
			"linkedin": "linkedinlink"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your social connection has been updated successfully')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

		social_account = SocialConnection.objects.get(user=self.user_1)
		self.assertEquals(social_account.twitter, context["twitter"])
		self.assertEquals(social_account.facebook, context["facebook"])
		self.assertEquals(social_account.google, context["google"])
		self.assertEquals(social_account.linkedin, context["linkedin"])

	def test_user_settings_block_IP_address(self):
		self.ip_response = requests.get("http://ip-api.com/json").json() 
		self.this_session = UserSession.objects.create(
			user=self.user_1,
			device_type="Chrome, Windows",
			location="Barking, England, United Kingdom",
			ip_address=self.ip_response['query']
		)
		# self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "block_unblock_IP",
			"session_id": self.this_session.pk,
			"allow": "false"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(ajax_reponse["message"], "{} has been blocked".format(self.this_session.ip_address))

	def test_user_settings_unblock_IP_address(self):
		self.ip_response = requests.get("http://ip-api.com/json").json() 
		self.this_session = UserSession.objects.create(
			user=self.user_1,
			device_type="Chrome, Windows",
			location="Barking, England, United Kingdom",
			ip_address=self.ip_response['query']
		)
		# self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "block_unblock_IP",
			"session_id": self.this_session.pk,
			"allow": "true"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(ajax_reponse["message"], "{} has been unblocked".format(self.this_session.ip_address))