# from accounts.seed_data_installer import installTutor
# from django.contrib.auth.models import User
# from django.test import Client
# from django.test import TestCase
# from django.urls import reverse
# from unittest import skip
#
# # coverage run --source='.' manage.py test accounts
# # coverage html
#
# @skip("Running multiple tests simultaneously slows down the process")
# class TestAccountViewsRegister(TestCase):
# 	"""
# 		Testing the register view where the user want to create an account.
# 	"""
#
# 	def setUp(self):
# 		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# 		self.url = reverse('accounts:register')
# 		self.user_1 = User.objects.get(email='barry.allen@yahoo.com')
#
# 	@classmethod
# 	def setUpClass(cls):
# 		super(TestAccountViewsRegister, cls).setUpClass()
# 		installTutor()
#
# 	def test_login_GET(self):
# 		response = self.client.get(self.url)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertTemplateUsed(response, 'accounts/registrationView.html')
#
# 	def test_register_account_exists(self):
# 		"""
# 			Testing whether an account already exists with the specified email address.
# 		"""
# 		context = {
# 			"email": 'barry.allen@yahoo.com',
# 			"password": 'RanDomPasWord56',
# 			"confirm_password": 'RanDomPasWord56',
# 			"first_name": "Henry",
# 			"last_name": "Allen"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("message", response.context)
# 		self.assertEquals(response.context["message"], "An account already exists for this email address!")
# 		self.assertIn("email", response.context)
# 		self.assertEquals(response.context["email"], 'barry.allen@yahoo.com')
# 		self.assertIn("firstname", response.context)
# 		self.assertEquals(response.context["firstname"], "Henry")
# 		self.assertIn("lastname", response.context)
# 		self.assertEquals(response.context["lastname"], "Allen")
# 		self.assertTemplateUsed(response, 'accounts/registrationView.html')
#
# 	def test_register_password_not_matching(self):
# 		"""
# 			Unique email address.
# 			Testing whether the password 1 and password 2 are matching.
# 		"""
# 		context = {
# 			"email": 'oliver.queen@yahoo.com',
# 			"password": 'RanDomPasWord56',
# 			"confirm_password": 'QWERTY1234Q',
# 			"first_name": "Oliver",
# 			"last_name": "Queen"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("message", response.context)
# 		self.assertEquals(response.context["message"], "Your passwords do not match!")
# 		self.assertIn("email", response.context)
# 		self.assertEquals(response.context["email"], 'oliver.queen@yahoo.com')
# 		self.assertIn("firstname", response.context)
# 		self.assertEquals(response.context["firstname"], "Oliver")
# 		self.assertIn("lastname", response.context)
# 		self.assertEquals(response.context["lastname"], "Queen")
# 		self.assertTemplateUsed(response, 'accounts/registrationView.html')
#
# 	def test_register_password_not_strong(self):
# 		"""
# 			Unique email address.
# 			Matching passwords.
# 			Testing whether the password is strong or not.
# 		"""
# 		context = {
# 			"email": 'oliver.queen@yahoo.com',
# 			"password": '123',
# 			"confirm_password": '123',
# 			"first_name": "Oliver",
# 			"last_name": "Queen"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("message", response.context)
# 		self.assertEquals(response.context["message"], "Your password is not strong enough.")
# 		self.assertIn("email", response.context)
# 		self.assertEquals(response.context["email"], 'oliver.queen@yahoo.com')
# 		self.assertIn("firstname", response.context)
# 		self.assertEquals(response.context["firstname"], "Oliver")
# 		self.assertIn("lastname", response.context)
# 		self.assertEquals(response.context["lastname"], "Queen")
# 		self.assertTemplateUsed(response, 'accounts/registrationView.html')
#
# 	def test_register_create_account(self):
# 		"""
# 			Unique email address.
# 			Matching passwords.
# 			Strong passwords.
# 			Testing whether we can create an account and an activation link is sent.
# 		"""
# 		context = {
# 			"email": 'oliver.queen@yahoo.com',
# 			"password": 'RanDomPasWord56',
# 			"confirm_password": 'RanDomPasWord56',
# 			"first_name": "Oliver",
# 			"last_name": "Queen"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("activate", response.context)
# 		self.assertEquals(response.context["activate"], "We've sent you an activation link. Please check your email.")
# 		self.assertTrue(User.objects.filter(username='oliver.queen@yahoo.com').exists())