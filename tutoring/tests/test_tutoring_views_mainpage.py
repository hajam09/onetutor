from unittest import skip
from django.test import TestCase, Client
from django.urls import reverse
from accounts.seed_data_installer import installTutor

# coverage run --source=accounts manage.py test tutoring
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestTutoringViewsMainpage(TestCase):
	"""
		Testing the mainpage of the application and the search results.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('tutoring:mainpage')
		installTutor()

	def test_mainpage_GET(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_empty_input(self):
		context = {
			"generalQuery": "",
			"location": ""
		}
		response = self.client.post(self.url, context)
		self.assertIn("message", response.context)
		self.assertEquals(response.context["message"], "Search for a tutor again!")
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-danger")
		self.assertNotIn("tutorList", response.context)
		self.assertNotIn("generalQuery", response.context)
		self.assertNotIn("location", response.context)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_invalid_input(self):
		"""
			Entering a tutor that does not exist in the db.
			Both the generalQuery and location will be specified.
		"""
		context = {
			"generalQuery": "random tutor",
			"location": "random location"
		}
		response = self.client.post(self.url, context)
		self.assertIn("generalQuery", response.context)
		self.assertIn("location", response.context)
		self.assertEquals(response.context["tutorList"].count(), 0)
		self.assertEquals(response.context["message"], "Sorry, we couldn't find you a tutor for your search. Try entering something broad.")
		self.assertEquals(response.context["alert"], "alert-info")
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_valid_generalQuery_and_location(self):
		"""
			Entering a tutor that does exist in the db.
			Both the generalQuery and location will be specified.
		"""
		context = {
			"generalQuery": "english",
			"location": "london"
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.context["generalQuery"], "english")
		self.assertEquals(response.context["location"], "london")
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_valid_generalQuery(self):
		"""
			Entering a tutor that does exist in the db.
			Only the generalQuery will be specified.
		"""
		context = {
			"generalQuery": "english",
			"location": ""
		}
		response = self.client.post(self.url, context)
		self.assertEquals(response.context["generalQuery"], "english")
		self.assertNotIn("location", response.context)
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_valid_location(self):
		"""
			Entering a tutor that does exist in the db.
			Only the location will be specified.
		"""
		context = {
			"generalQuery": "",
			"location": "london"
		}
		response = self.client.post(self.url, context)
		self.assertNotIn("generalQuery", response.context)
		self.assertEquals(response.context["location"], "london")
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")