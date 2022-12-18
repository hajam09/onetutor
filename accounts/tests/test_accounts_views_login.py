# from accounts.seed_data_installer import installTutor
# from django.contrib.auth.models import User
# from django.core.cache import cache
# from django.test import Client
# from django.test import TestCase
# from django.urls import reverse
# from unittest import skip
# import json
# import requests
#
# # coverage run --source='.' manage.py test accounts
# # coverage html
#
# @skip("Running multiple tests simultaneously slows down the process")
# class TestAccountViewsLogin(TestCase):
# 	"""
# 		Testing the login view where the user want to login to the system, and it's subsidiary function.
# 	"""
#
# 	def setUp(self):
# 		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# 		self.url = reverse('accounts:login-view')
# 		self.user_1 = User.objects.get(email='barry.allen@yahoo.com')
#
# 	@classmethod
# 	def setUpClass(cls):
# 		super(TestAccountViewsLogin, cls).setUpClass()
# 		installTutor()
#
# 	def test_login_GET(self):
# 		response = self.client.get(self.url)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertTemplateUsed(response, 'accounts/loginView.html')
#
# 	def test_login_rememberMe(self):
# 		"""
# 			Credentials are correct.
# 			Check if the session expiry time is 0
# 		"""
# 		pass
#
# 	# @skip("Don't want to test")
# 	def test_login_authenticate_valid_user(self):
# 		"""
# 			Credentials are correct.
# 		"""
# 		context = {
# 			"username": 'barry.allen@yahoo.com',
# 			"password": 'RanDomPasWord56',
# 			"browser_type": "Chrome"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEqual(response.status_code, 302)
# 		self.assertRedirects(response, '/')
# 		self.assertIn('_auth_user_id', self.client.session)
# 		self.assertEqual(int(self.client.session['_auth_user_id']), self.user_1.pk)
#
# 	# @skip("Don't want to test")
# 	def test_login_authenticate_invalid_user(self):
# 		"""
# 			Credentials are incorrect.
# 		"""
# 		context = {
# 			"username": 'nonexistentialuser@gmail.com',
# 			"password": 'QWERTY1234Q',
# 			"browser_type": "Chrome"
# 		}
# 		response = self.client.post(self.url, context)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("message", response.context)
# 		self.assertEquals(response.context["message"], "Username or Password did not match!")
# 		self.assertIn("username", response.context)
# 		self.assertEquals(response.context["username"], 'nonexistentialuser@gmail.com')
# 		self.assertTemplateUsed(response, "accounts/loginView.html")
#
# 	# @skip("Don't want to test")
# 	def test_logout(self):
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		self.url = reverse('accounts:logout')
# 		response = self.client.get(self.url)
# 		self.assertEqual(response.status_code, 302)
# 		self.assertRedirects(response, '/accounts/login/')
# 		self.assertNotIn('_auth_user_id', self.client.session)
#
# 	# @skip("Don't want to test")
# 	def test_login_login_attempts(self):
# 		"""
# 			Credentials are incorrect.
# 			User temporarily blocked from authenticating.
# 		"""
# 		context = {
# 			"username": 'nonexistentialuser@gmail.com',
# 			"password": 'QWERTY1234Q',
# 			"browser_type": "Chrome"
# 		}
#
# 		i = 0
# 		while True:
# 			response = self.client.post(self.url, context)
# 			i = i+1
# 			if i > 5:
# 				break
#
# 		self.assertNotEqual(cache.get('loginAttempts'), None)
# 		self.assertEqual(response.status_code, 200)
# 		self.assertIn("message", response.context)
# 		self.assertEquals(response.context["message"], "Your account has been temporarily locked out because of too many failed login attempts.")
# 		cache.set('loginAttempts', None)