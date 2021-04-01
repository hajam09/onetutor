from accounts.models import TutorProfile
from accounts.seed_data_installer import installTutor
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from tutoring.models import QuestionAnswer
from unittest import skip
import json

# coverage run --source=tutoring manage.py test tutoring
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestTutoringViewsTutorQuestions(TestCase):
	"""
		Testing the tutor question page, which lists all the question answer instances belonging to this tutor profile.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		installTutor()
		self.url = reverse('tutoring:tutor_questions')
		self.user1 = User.objects.get(email=AccountValueSet.USER_1_EMAIL)
		self.user2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.user3 = User.objects.create_user(username="test_uname", email="test_email", password="test_passwordM123", first_name="test_first_name", last_name="test_last_name")
		self.tutor_1_profile = TutorProfile.objects.get(user=self.user1)
		self.client.login(username='test_uname', password='test_passwordM123')
		
		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.user2,
			answerer=self.user1
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
		self.client.login(username=AccountValueSet.USER_1_EMAIL, password='RanDomPasWord56')
		response = self.client.get(self.url, {})
		self.assertIn("questionAndAnswers", response.context)
		self.assertEquals(list(response.context["questionAndAnswers"]), list(QuestionAnswer.objects.filter(answerer=self.user1).order_by('-id')))
		self.assertTemplateUsed(response, "tutoring/tutor_questions.html")

	def test_tutorquestion_post_answer_question_deleted(self):
		self.client.login(username=AccountValueSet.USER_1_EMAIL, password='RanDomPasWord56')
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
		self.client.login(username=AccountValueSet.USER_1_EMAIL, password='RanDomPasWord56')
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
		self.client.login(username=AccountValueSet.USER_1_EMAIL, password='RanDomPasWord56')
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
		self.client.login(username=AccountValueSet.USER_1_EMAIL, password='RanDomPasWord56')
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