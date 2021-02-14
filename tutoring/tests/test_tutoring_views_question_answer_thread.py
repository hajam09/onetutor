from unittest import skip
from django.test import TestCase, Client
from django.urls import reverse
from accounts.seed_data_installer import installTutor
from django.contrib.auth.models import User
from tutoring.models import QuestionAnswer, QAComment
import json

# coverage run --source=tutoring manage.py test tutoring
# coverage html

# @skip("Running multiple tests simultaneously slows down the process")
class TestTutoringViewsQuestionAnswerThread(TestCase):
	"""
		Testing the question answer thread.
		Thread created for each questions asked on the tutor profile.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		installTutor()
		self.user1 = User.objects.get(email='barry.allen@yahoo.com')
		self.user2 = User.objects.get(email='cisco.ramone@hotmail.com')
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')

		self.new_question = QuestionAnswer.objects.create(
			subject="Maths",
			question="What is the purpose of life?",
			answer="Not answered yet.",
			questioner=self.user2,
			answerer=self.user1
		)

		self.qaComment = QAComment.objects.create(
			question_answer = self.new_question,
			creator = self.user1,
			comment = 'Sample comment'
		)


		self.url = reverse('tutoring:question_answer_thread', kwargs={'question_id':self.new_question.id})

	def test_question_answer_thread_view_render(self):
		response = self.client.get(self.url, {})
		self.assertIn("qa", response.context)
		self.assertEquals(response.context["qa"], self.new_question)
		self.assertTemplateUsed(response, "tutoring/question_answer_thread.html")

	def test_question_answer_thread_post_comment(self):
		payload = {
			"functionality": "post_comment",
			"comment": "This is a brand new comment"
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		fields = json.loads(ajax_reponse["new_qa_comment"])[0]['fields']
		self.assertEquals(fields['creator'], self.user1.pk)
		self.assertEquals(fields['comment'], payload['comment'])

	def test_question_answer_thread_like_comment(self):
		payload = {
			"functionality": "like_comment",
			"commentId": self.qaComment.id
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)

		fields = json.loads(ajax_reponse["this_comment"])[0]['fields']
		self.assertTrue(self.user1.pk in fields["likes"])
		self.assertTrue(self.user1.pk not in fields["dislikes"])

	def test_question_answer_thread_like_comment_deleted(self):
		payload = {
			"functionality": "like_comment",
			"commentId": self.qaComment.id
		}

		self.qaComment.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this comment has been deleted!")

	def test_question_answer_thread_dislike_comment(self):
		payload = {
			"functionality": "dislike_comment",
			"commentId": self.qaComment.id
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)

		fields = json.loads(ajax_reponse["this_comment"])[0]['fields']
		self.assertTrue(self.user1.pk not in fields["likes"])
		self.assertTrue(self.user1.pk in fields["dislikes"])

	def test_question_answer_thread_dislike_comment_deleted(self):
		payload = {
			"functionality": "dislike_comment",
			"commentId": self.qaComment.id
		}

		self.qaComment.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this comment has been deleted!")

	def test_question_answer_thread_delete_qa_comment(self):
		payload = {
			"functionality": "delete_qa_comment",
			"comment_id": self.qaComment.id
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertFalse(QAComment.objects.filter(id=self.qaComment.id).exists())

	def test_question_answer_thread_delete_qa_comment_deleted(self):
		payload = {
			"functionality": "delete_qa_comment",
			"comment_id": self.qaComment.id
		}

		self.qaComment.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertFalse(QAComment.objects.filter(id=self.qaComment.id).exists())

	def test_question_answer_thread_update_comment(self):
		payload = {
			"functionality": "update_comment",
			"comment_id": self.qaComment.id,
			"comment_text": "Updated new comment"
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)

		fields = json.loads(ajax_reponse["this_comment"])[0]['fields']
		self.assertTrue(fields["edited"])
		self.assertEquals(fields["comment"], payload["comment_text"])

	def test_question_answer_thread_update_comment_deleted(self):
		payload = {
			"functionality": "update_comment",
			"comment_id": self.qaComment.id,
			"comment_text": "Updated new comment"
		}

		self.qaComment.delete()
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 404)
		self.assertEquals(ajax_reponse["message"], "We think this comment has been deleted!")

	def test_question_answer_thread_ajax_not_authenticated(self):
		self.client.logout()
		payload = {
			"functionality": "post_comment",
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to post a comment.")

		payload = {
			"functionality": "like_comment",
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to like the comment.")

		payload = {
			"functionality": "dislike_comment",
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to dislike the comment.")

		payload = {
			"functionality": "update_comment",
		}

		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 401)
		self.assertEquals(ajax_reponse["message"], "Login to update the comment.")