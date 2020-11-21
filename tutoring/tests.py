from django.test import TestCase, Client
from django.urls import reverse
from .models import QuestionAnswer
from django.contrib.auth.models import User
from accounts.models import TutorProfile
import json
# from accounts.seedDataInstaller import *

class TestViewsMainPage(TestCase):

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

class TestViewsViewTutorProfile(TestCase):

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
		self.tutor_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.tutor_1_profile = self.create_tutor_profile(self.tutor_1, "summary 1", "about 1", "English, Maths")
		self.tutor_2 = self.create_user("oliver.queen@yahoo.com", "oliver.queen@yahoo.com", "RanDomPasWord56", "Oliver", "Queen")
		self.tutor_2_profile = self.create_tutor_profile(self.tutor_2, "summary 2", "about 2", "English, ICT, RE")
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':self.tutor_1_profile.secondary_key})

	def test_viewtutorprofile_does_not_exist(self):
		"""
			Searching for a tutor that does not exist in the db.
		"""
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':'cd4df0b5-7500-4f97-83eb-586768a9c265'})
		response = self.client.get(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/')

	def test_viewtutorprofile_postQuestion_not_authenticated(self):
		"""
			Searching for a tutor that does exist in the db.
			The user is not authenticated.
		"""
		context = {
			"postQuestion": "",
			"subject": "Maths",
			"question": "What is the question?"
		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, "/accounts/login/")

	def test_viewtutorprofile_postQuestion_authenticated(self):
		"""
			Searching for a tutor that does exist in the db.
			The user is authenticated.
			The user is posting a question.
		"""
		context = {
			"postQuestion": "",
			"subject": "Maths",
			"question": "What is the question?"
		}
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		count_before = QuestionAnswer.objects.all().count()
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['request'].user.is_authenticated)
		self.assertEqual(QuestionAnswer.objects.all().count(), count_before + 1)
		self.assertIn("activeQATab", response.context)
		self.assertEquals(response.context["activeQATab"], True)
		self.assertIn("questionAndAnswers", response.context)
		self.assertTemplateUsed(response, "tutoring/tutorprofile.html")

	def test_viewtutorprofile_postAnswer_not_authenticated(self):
		"""
			Searching for a tutor that does exist in the db.
			The user is not authenticated.
		"""
		context = {
			"postAnswer": "",
			"subject": "Maths",
			"question": "What is the question?"
		}
		response = self.client.post(self.url, context)
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, "/accounts/login/")

	def test_viewtutorprofile_postAnswer_authenticated(self):
		"""
			Searching for a tutor that does exist in the db.
			The user is authenticated.
			The user is posting the answer.
		"""
		self.test_viewtutorprofile_postQuestion_authenticated() # just to login a user.
		random_question = str(QuestionAnswer.objects.all()[0].pk)
		context = {
			"postAnswer": "",
			"questionId": random_question,
			"answerText": "Making a reply to the answer"
		}
		response = self.client.post(self.url, context)
		self.assertIn("activeQATab", response.context)
		self.assertEquals(response.context["activeQATab"], True)
		self.assertIn("activeQuestion", response.context)
		self.assertEquals(response.context["activeQuestion"], random_question)
		self.assertIn("questionAndAnswers", response.context)
		self.assertTemplateUsed(response, "tutoring/tutorprofile.html")
		self.assertEquals(QuestionAnswer.objects.all()[0].answer, "Making a reply to the answer")

class TestViewsLikeComment(TestCase):

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
		self.url = reverse('tutoring:like_comment')
		self.tutor_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.tutor_1_profile = self.create_tutor_profile(self.tutor_1, "summary 1", "about 1", "English, Maths")
		self.tutor_2 = self.create_user("oliver.queen@yahoo.com", "oliver.queen@yahoo.com", "RanDomPasWord56", "Oliver", "Queen")
		self.tutor_2_profile = self.create_tutor_profile(self.tutor_2, "summary 2", "about 2", "English, ICT, RE")
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.tutor_1,
			answerer=self.tutor_2
		)

	def test_like_comment_not_ajax(self):
		"""
			User is not authenticated
			Making a POST request so it is not an AJAX request.
		"""
		response = self.client.post(self.url, {})
		ajax_reponse = json.loads(response.content) 
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 403)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], "Bad Request")

	def test_like_comment_not_authenticated(self):
		"""
			User is not authenticated
			Making an AJAX request.
		"""
		response = self.client.post(self.url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content) 
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], "Login to like the question and answer. ")

	def test_like_comment_add_like(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(1) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)

	def test_like_comment_remove_like(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User in list of liked.
			User not in list of disliked.
			L(1) : D(0) --> L(0) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		user.likes.add(self.new_question)
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)

	def test_like_comment_add_like_remove_dislike(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User not in list of liked.
			User in list of disliked.
			L(0) : D(1) --> L(1) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		user.dislikes.add(self.new_question)
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)


class TestViewsDislikeComment(TestCase):

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
		self.url = reverse('tutoring:dislike_comment')
		self.tutor_1 = self.create_user("barry.allen@yahoo.com", "barry.allen@yahoo.com", "RanDomPasWord56", "Barry", "Allen")
		self.tutor_1_profile = self.create_tutor_profile(self.tutor_1, "summary 1", "about 1", "English, Maths")
		self.tutor_2 = self.create_user("oliver.queen@yahoo.com", "oliver.queen@yahoo.com", "RanDomPasWord56", "Oliver", "Queen")
		self.tutor_2_profile = self.create_tutor_profile(self.tutor_2, "summary 2", "about 2", "English, ICT, RE")
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.tutor_1,
			answerer=self.tutor_2
		)

	def test_dislike_comment_not_ajax(self):
		"""
			User is not authenticated
			Making a POST request so it is not an AJAX request.
		"""
		response = self.client.post(self.url, {})
		ajax_reponse = json.loads(response.content) 
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 403)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], "Bad Request")

	def test_dislike_comment_not_authenticated(self):
		"""
			User is not authenticated
			Making an AJAX request.
		"""
		response = self.client.post(self.url, {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content) 
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], "Login to dislike the question and answer. ")

	def test_dislike_comment_add_dislike(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(0) : D(1)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)

	def test_dislike_comment_remove_dislike(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User not in list of liked.
			User in list of disliked.
			L(0) : D(1) --> L(0) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		user.dislikes.add(self.new_question)
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)

	def test_dislike_comment_add_dislike_remove_like(self):
		"""
			Making an AJAX request.
			User is authenticated.
			User in list of liked.
			User not in list of disliked.
			L(1) : D(0) --> L(0) : D(1)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		user = User.objects.get(username='barry.allen@yahoo.com')
		user.likes.add(self.new_question)
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=user.pk))
		self.assertIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=user.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)