from django.test import TestCase
from django.test import Client
from django.urls import reverse
from onetutor.tests.ForumTestHelper import ForumBuildHelper
from unittest import skip

# coverage run --source='.' manage.py test forum
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestForumViewsCommunitypage(TestCase):

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.forums = ForumBuildHelper()
		self.forums.communityBuilder(1)
		self.forums.forumBuilder(2)
		self.forums.forumCommentBuilder(4)
		self.url = reverse('forum:communitypage', kwargs={'community_id':self.forums.community[0].id})
		self.client.login(username=self.forums.newUser.user.username, password='RanDomPasWord56')

	@classmethod
	def setUpClass(cls):
		super(TestForumViewsCommunitypage, cls).setUpClass()
		

	def test_community_page_view_render(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertEquals(response.context["community"], self.forums.community[0])
		self.assertEquals(len(response.context["forums"]), len(self.forums.forum))
		self.assertFalse(response.context["in_community"])
		self.assertTemplateUsed(response, 'forum/communitypage.html')