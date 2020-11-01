from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from accounts.models import TutorProfile

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
	pass

class TestViewsTutorProfileEdit(TestCase):
	pass