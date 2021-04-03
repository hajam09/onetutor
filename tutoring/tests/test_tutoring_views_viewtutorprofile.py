from accounts.models import TutorProfile
from accounts.seed_data_installer import installTutor
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from tutoring.models import QuestionAnswer
from tutoring.models import TutorReview
from unittest import skip
import json

# coverage run --source='.' manage.py test tutoring
# coverage html

# @skip("Running multiple tests simultaneously slows down the process")
class TestTutoringViewsViewTutorProfile(TestCase):
	"""
		Testing the create tutor profile view of the application.
		New user creates a tutor profile object.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.user1 = User.objects.get(email='barry.allen@yahoo.com')
		self.user2 = User.objects.get(email='cisco.ramone@hotmail.com')

		self.tutor_1_profile = TutorProfile.objects.get(user=self.user1)
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':self.tutor_1_profile.secondary_key})

		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.user1,
			answerer=self.user2
		)

		self.new_tutor_review = TutorReview.objects.create(
			tutor=self.user2,
			reviewer=self.user1,
			comment="Test comment",
			rating=4
		)

	@classmethod
	def setUpClass(cls):
		super(TestTutoringViewsViewTutorProfile, cls).setUpClass()
		installTutor()

	def test_viewtutorprofile_does_not_exist(self):
		"""
			Searching for a tutor that does not exist in the db.
		"""
		self.url = reverse('tutoring:viewtutorprofile', kwargs={'tutor_secondary_key':'cd4df0b5-7500-4f97-83eb-586768a9c265'})
		response = self.client.get(self.url, {})
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/')

	def test_viewtutorprofile_render(self):
		"""
			Checking the context value it returns for a tutor profile.
		"""
		response = self.client.get(self.url, {})
		self.assertIn("tutorProfile", response.context)
		self.assertIn("subjects", response.context)
		self.assertIn("questionAndAnswers", response.context)
		self.assertEquals(response.context["tutorProfile"], self.tutor_1_profile)
		self.assertEquals(list(response.context["questionAndAnswers"]), list(QuestionAnswer.objects.filter(answerer=self.user1).order_by('-id')))
		self.assertTemplateUsed(response, "tutoring/tutorprofile.html")

	def test_viewtutorprofile_post_question_not_authenticated(self):
		"""
			User is posting a question on the tutor profile without logged in.
		"""
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
		"""
			User is posting a question on the tutor profile with proper permission.
		"""
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
		self.assertEquals(eval(ajax_reponse["new_qa"])[0]["fields"]["subject"], payload["subject"])
		self.assertEquals(eval(ajax_reponse["new_qa"])[0]["fields"]["question"], payload["question"])

	
	def test_viewtutorprofile_post_answer_not_authenticated(self):
		"""
			User is posting an answer on the tutor profile without logged in.
		"""
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
		"""
			User is posting an answer on the tutor profile.
			The question is deleted by the creator.
		"""
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
		self.assertEquals(ajax_reponse["message"], 'We think this question has been deleted!')

	def test_viewtutorprofile_post_answer_success(self):
		"""
			User is posting an answer on the tutor profile with proper permission.
		"""
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
		"""
			User/creator of the question is trying to delete the question they posted.
		"""
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
		"""
			User/creator of the question is trying to delete the question they posted.
			But that question is already deleted in an another window.
		"""
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
		"""
			User is updating the question text they created.
			But that question is already deleted in an another window.
		"""
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
		"""
			User is updating the question text they created.
		"""
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

	def test_viewtutorprofile_like_question_answer_object_not_authenticated(self):
		"""
			A random unauthenticated user is trying to like a question answer instance on the tutor profile.
		"""
		payload = {
			"functionality": "like_comment",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to like the question and answer. ")

	def test_viewtutorprofile_like_question_answer_object_not_found(self):
		"""
			Authenticated user is trying to like a question answer instance on the tutor profile.
			The question answer instance does not exist.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "like_comment",
			"commentId": self.new_question.pk,
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], 'We think this question has been deleted!')

	def test_viewtutorprofile_like_question_answer_object_success(self):
		"""
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(1) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "like_comment",
			"commentId": self.new_question.pk,
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

	def test_viewtutorprofile_dislike_question_answer_object_not_authenticated(self):
		"""
			A random unauthenticated user is trying to dislike a question answer instance on the tutor profile.
		"""
		payload = {
			"functionality": "dislike_comment",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to dislike the question and answer. ")

	def test_viewtutorprofile_dislike_question_answer_object_not_found(self):
		"""
			Authenticated user is trying to dislike a question answer instance on the tutor profile.
			The question answer instance does not exist.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "dislike_comment",
			"commentId": self.new_question.pk,
		}
		self.new_question.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], 'We think this question has been deleted!')

	def test_viewtutorprofile_dislike_question_answer_object_success(self):
		"""
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(0) : D(1)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "dislike_comment",
			"commentId": self.new_question.pk,
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

	def test_viewtutorprofile_delete_tutor_review_not_authenticated(self):
		"""
			User is deleting their own review made to a tutor without authentication.
			Could happen when logged out in one tab and deleting from another existing tab
			prior to user logging out
		"""
		payload = {
			"functionality": "delete_tutor_review"
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertIn("message", ajax_reponse)
		self.assertEquals(ajax_reponse["message"], 'Login to delete this review.')

	def test_viewtutorprofile_delete_tutor_review_successful(self):
		"""
			User is deleting their own review made to a tutor with authentication.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_tutor_review",
			"review_id": self.new_tutor_review.pk,
		}
		print("self.new_tutor_review.id", self.new_tutor_review.id)
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(TutorReview.objects.filter(id=self.new_tutor_review.id).count(), 0)

	def test_viewtutorprofile_delete_tutor_review_not_found(self):
		"""
			User/creator of the tutor reivew is trying to delete the review they posted.
			But that review is already deleted in an another window.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "delete_tutor_review",
			"review_id": self.new_tutor_review.pk,
		}
		self.new_tutor_review.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(TutorReview.objects.filter(id=self.new_tutor_review.id).count(), 0)

	def test_viewtutorprofile_like_tutor_review_object_not_authenticated(self):
		"""
			A random unauthenticated user is trying to like a tutor reivew instance on the tutor profile.
		"""
		payload = {
			"functionality": "like_tutor_review",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to like this tutor review.")

	def test_viewtutorprofile_like_tutor_review_object_not_found(self):
		"""
			Authenticated user is trying to like a tutor profile instance on the tutor profile.
			The instance does not exist.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "like_tutor_review",
			"review_id": self.new_tutor_review.pk,
		}
		self.new_tutor_review.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], 'We think this review has been deleted!')

	def test_viewtutorprofile_like_tutor_review_object_success(self):
		"""
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(1) : D(0)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "like_tutor_review",
			"review_id": self.new_tutor_review.pk,
		}		
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertIn(self.new_tutor_review, TutorReview.objects.filter(likes__id=self.user1.pk))
		self.assertNotIn(self.new_tutor_review, TutorReview.objects.filter(dislikes__id=self.user1.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_tutor_review", ajax_reponse)

	def test_viewtutorprofile_dislike_tutor_review_object_not_authenticated(self):
		"""
			A random unauthenticated user is trying to dislike a tutor review instance on the tutor profile.
		"""
		payload = {
			"functionality": "dislike_tutor_review",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to dislike this tutor review.")

	def test_viewtutorprofile_dislike_tutor_review_object_not_found(self):
		"""
			Authenticated user is trying to dislike a tutor review instance on the tutor profile.
			The instance does not exist.
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "dislike_tutor_review",
			"review_id": self.new_tutor_review.pk,
		}
		self.new_tutor_review.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], 'We think this review has been deleted!')

	def test_viewtutorprofile_dislike_tutor_review_object_success(self):
		"""
			User is authenticated.
			User not in list of liked.
			User not in list of disliked.
			L(0) : D(0) --> L(0) : D(1)
		"""
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		payload = {
			"functionality": "dislike_tutor_review",
			"commentId": self.new_tutor_review.pk,
		}	
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertNotIn(self.new_tutor_review, TutorReview.objects.filter(likes__id=self.user1.pk))
		self.assertIn(self.new_tutor_review, TutorReview.objects.filter(dislikes__id=self.user1.pk))
		self.assertEquals(response.status_code, 200)
		self.assertIn("status_code", ajax_reponse)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertIn("this_comment", ajax_reponse)