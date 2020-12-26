from django.test import TestCase, Client
from django.urls import reverse
from .models import QuestionAnswer
from django.contrib.auth.models import User
from accounts.models import TutorProfile
import json
from accounts.seed_data_installer import installTutor

# coverage run --source=tutoring manage.py test tutoring

class TestViewsMainPage(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('tutoring:mainpage')
		installTutor() # populates User object and TutorProfile objects from seed-data.

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
		self.assertEquals(response.context["message"], "Sorry, we couldn't find you a tutor for your search. Try entering something broad.")
		self.assertIn("alert", response.context)
		self.assertEquals(response.context["alert"], "alert-info")
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
	def setUp(self):
		self.client = Client()
		installTutor() # populates User object and TutorProfile objects from seed-data.
		self.u1 = User.objects.get(email='barry.allen@yahoo.com')
		self.u2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.tutor_1_profile = TutorProfile.objects.get(user=self.u1)
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':self.tutor_1_profile.secondary_key})
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.u1,
			answerer=self.u2
		)

	def test_viewtutorprofile_does_not_exist(self):
		"""
			Searching for a tutor that does not exist in the db.
		"""
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':'cd4df0b5-7500-4f97-83eb-586768a9c265'})
		response = self.client.get(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/')

	def test_viewtutorprofile_render(self):
		response = self.client.get(self.url, {})
		self.assertIn("tutorProfile", response.context)
		self.assertIn("subjects", response.context)
		self.assertIn("questionAndAnswers", response.context)
		self.assertEquals(response.context["tutorProfile"], self.tutor_1_profile)
		self.assertEquals(list(response.context["questionAndAnswers"]), list(QuestionAnswer.objects.filter(answerer=self.u1).order_by('-id')))
		self.assertTemplateUsed(response, "tutoring/tutorprofile.html")

	def test_viewtutorprofile_post_question_not_authenticated(self):
		payload = {
			"functionality": "post_question"
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], 'Login to post a question.')

	def test_viewtutorprofile_post_question_authenticated(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "post_question",
			"subject": "English",
			"question": "Some random English question?"
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("new_qa", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("created_date", ajax_reponse)
		self.assertEquals(ajax_reponse["questioner_first_name"], 'Barry')
		self.assertEquals(ajax_reponse["questioner_last_name"], 'Allen')
		self.assertNotEqual(QuestionAnswer.objects.filter(questioner=User.objects.get(username='barry.allen@yahoo.com')), 0)

	def test_viewtutorprofile_post_answer_not_authenticated(self):
		payload = {
			"functionality": "post_answer"
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], 'Login to post an answer.')

	def test_viewtutorprofile_post_answer_question_deleted(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "post_answer",
			"question_id": self.new_question.pk,
			"new_answer": "New answer for this question."
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this question has been deleted!")

	def test_viewtutorprofile_post_answer_success(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "post_answer",
			"question_id": self.new_question.pk,
			"new_answer": "New answer for this question."
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("this_qa", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(QuestionAnswer.objects.get(id=self.new_question.id).answer, payload["new_answer"])

	def test_viewtutorprofile_delete_question_success(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_question",
			"question_id": self.new_question.pk,
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(QuestionAnswer.objects.filter(id=self.new_question.id).count(), 0)

	def test_viewtutorprofile_delete_question_not_found(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_question",
			"question_id": self.new_question.pk,
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(QuestionAnswer.objects.filter(id=self.new_question.id).count(), 0)

	def test_viewtutorprofile_update_question_not_found(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "update_question",
			"question_id": self.new_question.pk,
			"new_subject": "Art",
			"new_question": "This is a new question for this question object"
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(QuestionAnswer.objects.filter(id=self.new_question.id).count(), 0)

	def test_viewtutorprofile_update_question_success(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "update_question",
			"question_id": self.new_question.pk,
			"new_subject": "Art",
			"new_question": "This is a new question for this question object"
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("this_qa", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(QuestionAnswer.objects.get(id=self.new_question.id).subject, payload["new_subject"])
		self.assertEquals(QuestionAnswer.objects.get(id=self.new_question.id).question, payload["new_question"])

class TestViewsLikeComment(TestCase):

	def setUp(self):
		self.client = Client()
		self.url = reverse('tutoring:like_comment')
		installTutor() # populates User object and TutorProfile objects from seed-data.
		u1 = User.objects.get(email='barry.allen@yahoo.com')
		u2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=u1,
			answerer=u2
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

	def test_like_comment_question_object_deleted(self):
		"""
			Making an AJAX request.
			User is authenticated.
			QuestionAnswer object is deleted while clicking the button.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this question has been deleted!")

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

	def setUp(self):
		self.client = Client()
		self.url = reverse('tutoring:dislike_comment')
		installTutor() # populates User object and TutorProfile objects from seed-data.
		u1 = User.objects.get(email='barry.allen@yahoo.com')
		u2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=u1,
			answerer=u2
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

	def test_dislike_comment_question_object_deleted(self):
		"""
			Making an AJAX request.
			User is authenticated.
			QuestionAnswer object is deleted while clicking the button.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"commentId": str(self.new_question.pk)
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this question has been deleted!")


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

class TestViewsTutorQuestions(TestCase):

	def setUp(self):
		self.client = Client()
		installTutor() # populates User object and TutorProfile objects from seed-data.
		self.url = reverse('tutoring:tutor_questions')
		self.u1 = User.objects.get(email='barry.allen@yahoo.com')
		self.u2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.u3 = User.objects.create_user(username="test_uname", email="test_email", password="test_passwordM123", first_name="test_first_name", last_name="test_last_name")
		self.tutor_1_profile = TutorProfile.objects.get(user=self.u1)
		self.client.login(username='test_uname', password='test_passwordM123')
		
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.u2,
			answerer=self.u1
		)

	def test_tutorquestion_tutor_profile_does_not_exist(self):
		"""
			User must be authenticated prior to calling the view.
			TutorProfile does not exist to the authenticated user.
		"""
		response = self.client.post(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/createprofile/')
		self.assertIn('_auth_user_id', self.client.session)

	def test_tutorquestion_render(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		response = self.client.get(self.url, {})
		self.assertIn("questionAndAnswers", response.context)
		self.assertEquals(list(response.context["questionAndAnswers"]), list(QuestionAnswer.objects.filter(answerer=self.u1).order_by('-id')))
		self.assertTemplateUsed(response, "tutoring/tutor_questions.html")

	def test_tutorquestion_post_answer_question_deleted(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "post_answer",
			"question_id": self.new_question.pk,
			"new_answer": "New answer for this question."
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this question has been deleted!")

	def test_tutorquestion_post_answer_success(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "post_answer",
			"question_id": self.new_question.pk,
			"new_answer": "New answer for this question."
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("this_qa", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(QuestionAnswer.objects.get(id=self.new_question.id).answer, payload["new_answer"])

	def test_tutorquestion_delete_question_success(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_question",
			"question_id": self.new_question.pk,
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(QuestionAnswer.objects.filter(id=self.new_question.id).count(), 0)

	def test_tutorquestion_delete_question_not_found(self):
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_question",
			"question_id": self.new_question.pk,
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(QuestionAnswer.objects.filter(id=self.new_question.id).count(), 0)