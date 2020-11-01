from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from accounts.models import TutorProfile, Countries
from tutoring.models import QuestionAnswer

class TestViewsLogin(TestCase):

	def create_user(self, u, e, p, f, l):
		return User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)

	def setUp(self):
		self.client = Client()
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
			"password": "qWeRtY1234"
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
			"password": "RanDomPasWord56"
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
			"password": "qWeRtY1234"
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
			user=u, userType="TUTOR",
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

	def test_tutorprofile_update_personal_details(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
		"""
		context = {
			"updatePersonalDetails": "",
			"first_name": "Adrian",
			"last_name": "Chase"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("tutorProfile", response.context)
		self.assertEquals(response.context["tutorProfile"], TutorProfile.objects.get(user=self.user_1))
		self.assertIn("countries", response.context)
		self.assertCountEqual(response.context["countries"], Countries.objects.all())
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your personal details has been updated successfully")
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-success")
		self.assertIn("activeAccountTab", response.context)
		self.assertEquals(response.context["activeAccountTab"], True)
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")

		self.user_1 = User.objects.get(email="barry.allen@yahoo.com")
		self.assertEquals(self.user_1.first_name, context["first_name"])
		self.assertEquals(self.user_1.last_name, context["last_name"])

	def test_tutorprofile_update_personal_details_upload_profile_picture(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			Uploading a profile picture for the tutor profile.
		"""
		pass

	def test_tutorprofile_update_password_mismatch(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User current password confirmation not matching.
		"""
		context = {
			"updatePassword": "",
			"currentPassword": "RanDomPasWord99",
			"newPassword": "Strong98183",
			"confirmPassword": "Strong98183"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-danger")
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")
		self.assertIn("tutorProfile", response.context)
		self.assertEquals(response.context["tutorProfile"], TutorProfile.objects.get(user=self.user_1))
		self.assertIn("countries", response.context)
		self.assertCountEqual(response.context["countries"], Countries.objects.all())
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your current password does not match")
		self.assertIn("activeAccountTab", response.context)
		self.assertEquals(response.context["activeAccountTab"], True)

	def test_tutorprofile_update_password_mismatch_2(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User current password confirmation does match.
			User's new password and confirmation password does not match.
		"""
		context = {
			"updatePassword": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "Strong98183",
			"confirmPassword": "Strong76456"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-danger")
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")
		self.assertIn("tutorProfile", response.context)
		self.assertEquals(response.context["tutorProfile"], TutorProfile.objects.get(user=self.user_1))
		self.assertIn("countries", response.context)
		self.assertCountEqual(response.context["countries"], Countries.objects.all())
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your new password and confirm password does not match")
		self.assertIn("activeAccountTab", response.context)
		self.assertEquals(response.context["activeAccountTab"], True)

	def test_tutorprofile_update_weak_password(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User current password confirmation does match.
			User's new password and confirmation password does match.
			User's new password is weak.
		"""
		context = {
			"updatePassword": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "123",
			"confirmPassword": "123"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-warning")
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")
		self.assertIn("tutorProfile", response.context)
		self.assertEquals(response.context["tutorProfile"], TutorProfile.objects.get(user=self.user_1))
		self.assertIn("countries", response.context)
		self.assertCountEqual(response.context["countries"], Countries.objects.all())
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Your new password is not strong enough.")
		self.assertIn("activeAccountTab", response.context)
		self.assertEquals(response.context["activeAccountTab"], True)

	def test_tutorprofile_update_password_authenticate(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does exist to the authenticated user.
			User current password confirmation does match.
			User's new password and confirmation password does match.
			User's new password is strong.
			User should be authenticated after changing password.
		"""
		context = {
			"updatePassword": "",
			"currentPassword": "RanDomPasWord56",
			"newPassword": "RanDomPasWord123",
			"confirmPassword": "RanDomPasWord123"
		}
		self.user_1_profile = self.create_tutor_profile(self.user_1, "summary 1", "about 1", "English, Maths")
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 200)
		self.assertIn('_auth_user_id', self.client.session)
		self.assertTemplateUsed(response, "accounts/tutorprofile.html")
		self.assertIn("tutorProfile", response.context)
		self.assertEquals(response.context["tutorProfile"], TutorProfile.objects.get(user=self.user_1))
		self.assertIn("countries", response.context)
		self.assertCountEqual(response.context["countries"], Countries.objects.all())
		self.assertIn("questionAndAnswers", response.context)
		self.assertCountEqual(response.context["questionAndAnswers"], QuestionAnswer.objects.filter(answerer=self.user_1))

class TestViewsTutorProfileEdit(TestCase):
	pass