import random

from essential_generators import DocumentGenerator

from forum.models import Category
from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from onetutor.tests.UserDataHelper import NewUser


class ForumBuildHelper:

	def __init__(self):
		self.category = self.categoryBuilder()
		self.community = []
		self.forum = []
		self.forumComment = []
		self.newUser = NewUser()

	def categoryBuilder(self):
		return Category.objects.create(name="Other")

	def communityBuilder(self, totalValue):
		communityList = []
		for i in range(totalValue):
			communityList.append(
				Community.objects.create(
					creator = self.newUser.user,
					community_title = "community title",
					community_url = "community url",
					community_description = "community description",

				)
			)
		# Community.objects.bulk_create(communityList)
		self.community = communityList

	def forumBuilder(self, totalValue):
		forumList = []
		for i in range(totalValue):
			forumList.append(
				Forum.objects.create(
					community = random.choice(self.community),
					creator = self.newUser.user,
					forum_title = "forum title",
					forum_url = "forum url",
					forum_description = "forum description",
				)
			)
		# Forum.objects.bulk_create(forumList)
		self.forum = forumList

	def forumCommentBuilder(self, totalValue):
		forumCommentList = []
		for i in range(totalValue):
			gen = DocumentGenerator()
			forum = random.choice(self.forum)
			comment_description = gen.paragraph()

			forumCommentList.append(
				ForumComment(
					forum=forum,
					creator=self.newUser.user,
					comment_description=comment_description,
				)
			)
		ForumComment.objects.bulk_create(forumCommentList)
		self.forumComment = forumCommentList