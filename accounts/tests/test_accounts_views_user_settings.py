from accounts.models import Countries
from accounts.models import SocialConnection
from accounts.models import TutorProfile
from accounts.seed_data_installer import installCountries
from accounts.seed_data_installer import installTutor
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from tutoring.models import QuestionAnswer
from unittest import skip
import json
import requests

# coverage run --source='.' manage.py test accounts
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestAccountViewsUserSettings(TestCase):
	"""
		Testing the user settings view where the user can access their system settings.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('accounts:user_settings')
		self.user_1 = User.objects.get(email='barry.allen@yahoo.com')
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')

	@classmethod
	def setUpClass(cls):
		super(TestAccountViewsUserSettings, cls).setUpClass()
		installTutor()
		installCountries()

	def test_usersettings_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'accounts/user_settings.html')

	# @skip('')
	def test_usersettings_user_update_general_information(self):
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
		response = self.client.post(self.url, context)
		user = User.objects.get(username='barry.allen@yahoo.com')
		self.assertEqual(user.first_name, context["first_name"])
		self.assertEqual(user.last_name, context["last_name"])
		self.assertEqual(response.status_code, 302)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your personal details has been updated successfully')
		self.assertRedirects(response, '/accounts/user_settings/')

	# @skip('')
	def test_usersettings_user_tutorprofile_update_address(self):
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
			"stateProvince": "Essex",
			"postalZip": "YM5 2DG",
			"country": "GB"
		}
		response = self.client.post(self.url, context)
		tutor_profile = TutorProfile.objects.get(user=self.user_1)
		new_location = {
			"address_1": context["address_1"],
			"address_2": context["address_2"],
			"city": context["city"],
			"stateProvince": context["stateProvince"],
			"postalZip": context["postalZip"],
			"country": {"alpha": "GB", "name": "United Kingdom"}
		}
		self.assertEqual(tutor_profile.location, new_location)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your location has been updated successfully')
		self.assertEquals(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_usersettings_user_delete_account(self):
		"""
			A code is sent to their email and stored in the session.
			User trying to delete their account by entering the delete code.
		"""

		# Create the delete code and store it in the session
		response = self.client.get(reverse("accounts:request_delete_code"), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(ajax_reponse["message"], "Check your email for the code." )

		session = self.client.session


		context = {
			"delete_account": "",
			"delete-code": session["user_" + str(self.user_1.id) + "_delete_key"]
		}
		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Account deleted successfully')
		self.assertRedirects(response, '/')
		self.assertEqual(User.objects.filter(email='barry.allen@yahoo.com').count(), 0)

	def test_usersettings_user_update_password_mismatch_password(self):
		"""
			User is trying to change their password.
			But the current password input is incorrect.
		"""

		context = {
			"update_password": "",
			"currentPassword": "not_the_current_password",
			"newPassword": 'RanDomPasWord65',
			"confirmPassword": 'RanDomPasWord65'
		}

		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your current password does not match')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_usersettings_user_update_password_newpassword_confirmpassowrd_unmatched(self):
		"""
			User must be authenticated prior to calling the view.
			User trying to update their password.
			Users new password and confirm password is unmatched
		"""

		context = {
			"update_password": "",
			"currentPassword": 'RanDomPasWord56',
			"newPassword": 'RanDomPasWord65',
			"confirmPassword": "RanDomPasWord66"
		}

		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your new password and confirm password does not match')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_usersettings_user_update_password_weak_password(self):
		"""
			User is trying to change their password.
			Current password is correct, the new password and the confirm password is matched.
			The new password is not strong enough
		"""

		context = {
			"update_password": "",
			"currentPassword": 'RanDomPasWord56',
			"newPassword": '123',
			"confirmPassword": '123'
		}

		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your new password is not strong enough')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

	def test_usersettings_user_update_password_success(self):
		"""
			User is trying to change their password and is successful.
			Current password is correct, the new password and the confirm password is matched.
			Users new password passes all checklist.
		"""

		context = {
			"update_password": "",
			"currentPassword": 'RanDomPasWord56',
			"newPassword": 'RanDomPasWord65',
			"confirmPassword": 'RanDomPasWord65'
		}

		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your password has been updated')
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'accounts/user_settings.html')

	def test_usersettings_user_update_password_successfully_error_authenticating(self):
		"""
			User is trying to change their password and is successful.
			Current password is correct, the new password and the confirm password is matched.
			The new password is very strong and has been changed.
			The authentication after changing the pass has failed.
		"""
		pass

	def test_usersettings_user_add_update_social_links(self):
		"""
			User is trying to add or edit their social links.
		"""

		context = {
			"social_links": "",
			"twitter": "twitter/link",
			"facebook": "facebook/link",
			"google": "google/link",
			"linkedin": "linkedin/link"
		}

		response = self.client.post(self.url, context)
		messages = list(get_messages(response.wsgi_request))
		self.assertEqual(len(messages), 1)
		self.assertEqual(str(messages[0]), 'Your social connection has been updated successfully')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/user_settings/')

		social_account = SocialConnection.objects.get(user=self.user_1)
		self.assertEquals(social_account.twitter, context["twitter"])
		self.assertEquals(social_account.facebook, context["facebook"])
		self.assertEquals(social_account.google, context["google"])
		self.assertEquals(social_account.linkedin, context["linkedin"])