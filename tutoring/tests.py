from django.test import TestCase, Client
from django.urls import reverse
from .models import QuestionAnswer
from django.contrib.auth.models import User
from accounts.models import TutorProfile
# from accounts.seedDataInstaller import *

class TestViewsMainpage(TestCase):

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
		
		return TutorProfile.objects.create(user=u, userType="TUTOR",
										summary=s, about=a, location=location,
										education=education, subjects=su,
										availability=availability, profilePicture=None)

	def setUp(self):
		self.client = Client()
		self.url = reverse('tutoring:mainpage')
		self.tutor_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.tutor_1_profile = self.create_tutor_profile(self.tutor_1, "summary 1", "about 1", "English, Maths")
		self.tutor_2 = self.create_user("oliver.queen@yahoo.com", "oliver.queen@yahoo.com", "RanDomPasWord56", "Oliver", "Queen")
		self.tutor_2_profile = self.create_tutor_profile(self.tutor_2, "summary 2", "about 2", "English, ICT, RE")

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
		self.assertIn("alert", response.context)
		self.assertNotIn("tutorList", response.context)
		self.assertNotIn("generalQuery", response.context)
		self.assertNotIn("location", response.context)

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
		self.assertIn("tutorList", response.context)
		self.assertEquals(response.context["tutorList"].count(), 0)
		self.assertIn("message", response.context)
		self.assertIn("alert", response.context)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")

	def test_mainpage_POST_valid_generalQuery_location(self):
		"""
			Entering a tutor that does exist in the db.
			Both the generalQuery and location will be specified.
		"""
		context = {
			"generalQuery": "english",
			"location": "london"
		}
		response = self.client.post(self.url, context)
		self.assertIn("generalQuery", response.context)
		self.assertEquals(response.context["generalQuery"], "english")
		self.assertIn("location", response.context)
		self.assertEquals(response.context["location"], "london")
		self.assertIn("tutorList", response.context)
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
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
		self.assertIn("generalQuery", response.context)
		self.assertEquals(response.context["generalQuery"], "english")
		self.assertNotIn("location", response.context)
		self.assertIn("tutorList", response.context)
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
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
		self.assertIn("location", response.context)
		self.assertEquals(response.context["location"], "london")
		self.assertIn("tutorList", response.context)
		self.assertNotEquals(response.context["tutorList"].count(), 0)
		self.assertNotIn("message", response.context)
		self.assertNotIn("alert", response.context)
		self.assertTemplateUsed(response, "tutoring/mainpage.html")