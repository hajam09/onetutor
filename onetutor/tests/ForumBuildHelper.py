import random

from django.template.defaultfilters import slugify
from faker import Faker

from forum.models import Category
from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from onetutor.operations import generalOperations
from onetutor.tests import userDataHelper


class ForumBuildHelper:

    def __init__(self):
        self.category = self.categoryBuilder()
        self.community = []
        self.forum = []
        self.forumComment = []
        self.user = userDataHelper.createNewUser()
        self.faker = Faker()

    def categoryBuilder(self):
        return Category.objects.create(name="Other")

    def communityBuilder(self, totalValue=10):
        communityList = []
        for i in range(totalValue):
            title = self.faker.sentence(nb_words=2)
            url = slugify(title + " " + generalOperations.generateRandomString())

            communityList.append(
                Community(
                    creator=self.user,
                    title=title,
                    url=url,
                    tags="Tags",
                    description=self.faker.paragraph(nb_sentences=5),
                    banner=None,
                    logo=None,
                )
            )
        self.community = Community.objects.bulk_create(communityList)

    def forumBuilder(self, totalValue=50):
        forumList = []
        for i in range(totalValue):
            title = self.faker.sentence(nb_words=5)
            url = slugify(title + " " + generalOperations.generateRandomString())

            forumList.append(
                Forum(
                    community=random.choice(self.community),
                    creator=self.user,
                    title=title,
                    url=url,
                    description=self.faker.paragraph(nb_sentences=15),
                    image=None
                )
            )
        self.forum = Forum.objects.bulk_create(forumList)

    def forumCommentBuilder(self, totalValue=150):
        forumCommentList = []
        for i in range(totalValue):
            forumCommentList.append(
                ForumComment(
                    forum=random.choice(self.forum),
                    creator=self.user,
                    description=self.faker.paragraph(nb_sentences=15),
                )
            )
        self.forumComment = ForumComment.objects.bulk_create(forumCommentList)
