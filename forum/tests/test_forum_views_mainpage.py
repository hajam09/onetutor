from accounts.seed_data_installer import installCategories
from accounts.seed_data_installer import installCommunity
from accounts.seed_data_installer import installForum
from accounts.seed_data_installer import installTutor
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from forum.models import Category
from forum.models import Community
from forum.models import Forum
from unittest import skip
import json

# coverage run --source='.' manage.py test forum
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestForumViewsMainpage(TestCase):

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('forum:mainpage')
		self.user_1 = User.objects.get(email='barry.allen@yahoo.com')

	@classmethod
	def setUpClass(cls):
		super(TestForumViewsMainpage, cls).setUpClass()
		installTutor()
		installCategories()
		installCommunity(2)
		installForum(2)

	def test_mainpage_view_render(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["category"].count(), 15)
		self.assertEquals(len(response.context["forums"]), 2)
		self.assertTemplateUsed(response, 'forum/mainpage.html')

	def test_mainpage_POST_create_community_not_authenticated(self):
		context = {
			"create_community": "",
		}
		response = self.client.post(self.url, context)
		self.assertRedirects(response, '/accounts/login/')

	def test_mainpage_POST_create_community_success(self):
		context = {
			"create_community": "",
			"studyLevel": Category.objects.get(id=1).name,
			"title": "test title",
			"description": "test description",
		}
		old_count = Community.objects.count()
		self.client.login(username='barry.allen@yahoo.com', password='RanDomPasWord56')
		response = self.client.post(self.url, context)
		self.assertLess(old_count, Community.objects.count())
		self.assertRedirects(response, '/forum/c/{}/'.format(Community.objects.latest('id').pk))

	def test_mainpage_ajax_fetch_forums_index_1(self):
		payload = {
			"functionality": "fetch_forums",
			"next_index": "0",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["status_code"], 200)
		self.assertEquals(len(ajax_reponse["forum_json"]), 2)

	def test_mainpage_ajax_fetch_forums_index_error(self):
		payload = {
			"functionality": "fetch_forums",
			"next_index": "1",
		}
		response = self.client.get(self.url, payload, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		ajax_reponse = json.loads(response.content)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(ajax_reponse["error"], "IndexError")