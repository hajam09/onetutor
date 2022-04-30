import json

from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests import userDataHelper
from onetutor.tests.BaseTestAjax import BaseTestAjax
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment


class QuestionAnswerThreadViewTest(BaseTestAjax):

    def setUp(self) -> None:
        # TODO: Try to move this to the classmethod to initialise it one time
        temporaryUser = userDataHelper.createNewUser()
        self.questionAnswer = QuestionAnswer.objects.create(
            subject="subject",
            question="question",
            questioner=temporaryUser,
            answerer=temporaryUser
        )

        super(QuestionAnswerThreadViewTest, self).setUp(
            reverse('tutoring:question-answer-thread', kwargs={'questionId': self.questionAnswer.id}))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        self.questionAnswer.questioner = self.request.user

        self.questionAnswerComment = QuestionAnswerComment.objects.create(
            questionAnswer=self.questionAnswer,
            creator=self.request.user,
            comment="Sample comment"
        )

        self.currentQuestionAnswerCommentCount = QuestionAnswerComment.objects.count()

    @classmethod
    def setUpClass(cls):
        super(QuestionAnswerThreadViewTest, cls).setUpClass()

    def testCreateQuestionAnswerComment(self):
        testParams = self.TestParams("createQuestionAnswerComment", None, "Sample Comment")
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        newComment = ajaxResponse['newComment']

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(newComment["commentId"], self.currentQuestionAnswerCommentCount + 1)
        self.assertEquals(newComment["creatorFullName"], self.questionAnswerComment.creator.get_full_name())
        self.assertEquals(newComment["comment"], testParams.comment)
        # self.assertEquals(newComment["date"], testParams.comment)
        self.assertEquals(newComment["likeCount"], 0)
        self.assertEquals(newComment["dislikeCount"], 0)
        self.assertFalse(newComment["edited"])
        self.assertTrue(newComment["canEdit"])

    def testDeleteQuestionAnswerComment(self):
        testParams = self.TestParams("deleteQuestionAnswerComment", self.questionAnswerComment.id, None)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertFalse(QuestionAnswerComment.objects.filter(id=self.questionAnswerComment.id).exists())

    def testUpdateQuestionAnswerComment(self):
        testParams = self.TestParams("updateQuestionAnswerComment", self.questionAnswerComment.id,
                                     "Updated new comment")
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        updatedComment = ajaxResponse["updatedComment"]
        self.questionAnswerComment.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(updatedComment["commentId"], self.questionAnswerComment.id)
        self.assertEquals(updatedComment["comment"], "Updated new comment")
        self.assertTrue(updatedComment["edited"])
        self.assertTrue(self.questionAnswerComment.edited)
        self.assertEquals(self.questionAnswerComment.comment, "Updated new comment")

    def testLikeQuestionAnswerComment(self):
        testParams = self.TestParams("likeQuestionAnswerComment", self.questionAnswerComment.id, None)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        self.questionAnswerComment.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 1)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertEquals(self.questionAnswerComment.likes.count(), 1)
        self.assertEquals(self.questionAnswerComment.dislikes.count(), 0)

    def testDislikeQuestionAnswerComment(self):
        testParams = self.TestParams("dislikeQuestionAnswerComment", self.questionAnswerComment.id, None)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        self.questionAnswerComment.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 1)
        self.assertEquals(self.questionAnswerComment.likes.count(), 0)
        self.assertEquals(self.questionAnswerComment.dislikes.count(), 1)


    class TestParams:

        def __init__(self, functionality, commentId=None, comment=None):
            self.functionality = functionality
            self.commentId = commentId
            self.comment = comment

        def getData(self):
            data = {
                'functionality': self.functionality,
            }
            if self.commentId is not None:
                data['commentId'] = self.commentId
            if self.comment is not None:
                data['comment'] = self.comment
            return data
