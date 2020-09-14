# from accounts.seed_data_installer import installTutor
# from django.contrib.auth.models import User
# from django.test import TestCase, Client
# from django.urls import reverse
# from tutoring.models import QuestionAnswer
# from unittest import skip
# import json
#
# # coverage run --source='.' manage.py test tutoring
# # coverage html
#
# @skip("Running multiple tests simultaneously slows down the process")
# class TestTutoringAjaxMethodLikeQuestionAnswer(TestCase):
# 	"""
# 		Separate ajax method was created to like question answer instance.
# 	"""
#
# 	def setUp(self):
# 		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# 		self.user1 = User.objects.get(email='barry.allen@yahoo.com')
# 		self.user2 = User.objects.get(email='cisco.ramone@hotmail.com')
# 		self.url = reverse('tutoring:like_comment')
#
# 		self.new_question = QuestionAnswer.objects.create(
# 			subject="Maths",
# 			question="What is the purpose of life?",
# 			answer="Not answered yet.",
# 			questioner=self.user1,
# 			answerer=self.user2
# 		)
#
# 	@classmethod
# 	def setUpClass(cls):
# 		super(TestTutoringAjaxMethodLikeQuestionAnswer, cls).setUpClass()
# 		installTutor()
#
# 	def test_like_comment_method_like_question_answer_object_not_authenticated(self):
# 		"""
# 			A random unauthenticated user is trying to like a question answer instance.
# 		"""
# 		payload = {
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertEquals(ajax_reponse["status_code"], 401)
# 		self.assertEquals(ajax_reponse["message"], "Login to like the question and answer. ")
#
# 	def test_like_comment_method_like_question_answer_object_not_found(self):
# 		"""
# 			Authenticated user is trying to like a question answer instance.
# 			The question answer instance does not exist.
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
# 		self.new_question.delete()
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertEquals(ajax_reponse["status_code"], 404)
# 		self.assertEquals(ajax_reponse["message"], 'We think this question has been deleted!')
#
# 	def test_like_comment_method_like_question_answer_object_success(self):
# 		"""
# 			User is authenticated.
# 			User not in list of liked.
# 			User not in list of disliked.
# 			L(0) : D(0) --> L(1) : D(0)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)
#
# 	def test_like_comment_method_like_question_answer_object_remove_like(self):
# 		"""
# 			User is authenticated.
# 			User in list of liked.
# 			User not in list of disliked.
# 			L(1) : D(0) --> L(0) : D(0)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		self.new_question.likes.add(self.user1)
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)
#
# 	def test_like_comment_method_like_question_answer_object_remove_dislike(self):
# 		"""
# 			User is authenticated.
# 			User in list of liked.
# 			User not in list of disliked.
# 			L(0) : D(1) --> L(1) : D(0)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		self.new_question.dislikes.add(self.user1)
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)
#
# @skip("Running multiple tests simultaneously slows down the process")
# class TestTutoringAjaxMethodDislikeQuestionAnswer(TestCase):
# 	"""
# 		Separate ajax method was created to dislike question answer instance.
# 	"""
#
# 	def setUp(self):
# 		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
# 		self.user1 = User.objects.get(email='barry.allen@yahoo.com')
# 		self.user2 = User.objects.get(email='cisco.ramone@hotmail.com')
# 		self.url = reverse('tutoring:dislike_comment')
#
# 		self.new_question = QuestionAnswer.objects.create(
# 			subject="Maths",
# 			question="What is the purpose of life?",
# 			answer="Not answered yet.",
# 			questioner=self.user1,
# 			answerer=self.user2
# 		)
#
# 	@classmethod
# 	def setUpClass(cls):
# 		super(TestTutoringAjaxMethodDislikeQuestionAnswer, cls).setUpClass()
# 		installTutor()
#
# 	def test_dislike_comment_method_dislike_question_answer_object_not_authenticated(self):
# 		"""
# 			A random unauthenticated user is trying to dislike a question answer instance.
# 		"""
# 		payload = {
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertEquals(ajax_reponse["status_code"], 401)
# 		self.assertEquals(ajax_reponse["message"], "Login to dislike the question and answer. ")
#
# 	def test_dislike_comment_method_like_question_answer_object_not_found(self):
# 		"""
# 			Authenticated user is trying to dislike a question answer instance.
# 			The question answer instance does not exist.
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
# 		self.new_question.delete()
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertEquals(response.status_code, 200)
# 		self.assertEquals(ajax_reponse["status_code"], 404)
# 		self.assertEquals(ajax_reponse["message"], 'We think this question has been deleted!')
#
# 	def test_dislike_comment_method_dislike_question_answer_object_success(self):
# 		"""
# 			User is authenticated.
# 			User not in list of liked.
# 			User not in list of disliked.
# 			L(0) : D(0) --> L(0) : D(1)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)
#
# 	def test_dislike_comment_method_dislike_question_answer_object_remove_dislike(self):
# 		"""
# 			User is authenticated.
# 			User in list of liked.
# 			User not in list of disliked.
# 			L(0) : D(1) --> L(0) : D(0)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		self.new_question.dislikes.add(self.user1)
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)
#
# 	def test_dislike_comment_method_dislike_question_answer_object_remove_like(self):
# 		"""
# 			User is authenticated.
# 			User in list of liked.
# 			User not in list of disliked.
# 			L(1) : D(0) --> L(0) : D(0)
# 		"""
# 		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
# 		self.new_question.likes.add(self.user1)
# 		payload = {
# 			"commentId": self.new_question.pk,
# 		}
#
# 		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 		ajax_reponse = json.loads(response.content)
# 		self.assertNotIn(self.new_question, QuestionAnswer.objects.filter(likes__id=self.user1.pk))
# 		self.assertIn(self.new_question, QuestionAnswer.objects.filter(dislikes__id=self.user1.pk))
# 		self.assertEquals(response.status_code, 200)
# 		self.assertIn("status_code", ajax_reponse)
# 		self.assertEquals(ajax_reponse["status_code"], 200)
# 		self.assertIn("this_comment", ajax_reponse)