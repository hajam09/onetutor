from accounts.seed_data_installer import installCategories
from accounts.seed_data_installer import installTutor
from accounts.seed_data_installer import installForum
from django.contrib.auth.models import User
from forum.models import Community
from django.test import TestCase, Client
from django.urls import reverse
from forum.models import Category
from unittest import skip

# coverage run --source='.' manage.py test forum
# coverage html

# @skip("Running multiple tests simultaneously slows down the process")
class TestForumViewsMainpage(TestCase):

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('forum:mainpage')
		self.user_1 = User.objects.get(email='barry.allen@yahoo.com')

	@classmethod
	def setUpClass(cls):
		super(TestForumViewsMainpage, cls).setUpClass()
		installCategories()
		installTutor()
		installForum(20)

	def test_mainpage_view_render(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["category"].count(), Category.objects.count())
		self.assertEquals(response.context["forums"], [])
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
		self.assertRedirects(response, '/forum/c/1/')