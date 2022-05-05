import json
from http import HTTPStatus

from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests import userDataHelper
from onetutor.tests.BaseTestAjax import BaseTestAjax
from tutoring.models import QuestionAnswer, TutorReview


class TutoringViewTutorProfileView(BaseTestAjax):

    def setUp(self) -> None:
        self.tutorProfile = userDataHelper.createTutorProfileForUser(userDataHelper.createNewUser())
        super(TutoringViewTutorProfileView, self).setUp(
            reverse('tutoring:view-tutor-profile', kwargs={'url': self.tutorProfile.url})
        )
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

        self.questionAnswer = QuestionAnswer.objects.create(
            subject="subject",
            question="question",
            questioner=self.user,
            answerer=self.tutorProfile.user
        )

        self.tutorReview = TutorReview.objects.create(
            tutor=self.tutorProfile.user,
            reviewer=self.request.user,
            comment="comment",
            rating=2,
        )

    def testUserNotAuthenticated(self):
        self.client.logout()
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(ajaxResponse["statusCode"], HTTPStatus.UNAUTHORIZED)

    def testPostQuestionAnswer(self):
        testParams = self.TestParamsQuestionAnswer("postQuestionAnswer")
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        questionAnswer = QuestionAnswer.objects.last()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["questionerFullName"], self.user.get_full_name())
        # self.assertEquals(ajaxResponse["createdDate"], self.user.get_full_name())
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertEquals(questionAnswer.subject, "English")
        self.assertEquals(questionAnswer.question, "Question")
        self.assertEquals(questionAnswer.questioner, self.user)
        self.assertEquals(questionAnswer.answerer, self.tutorProfile.user)

    def testAnswerQuestionAnswerSuccess(self):
        self.client.logout()
        self.client.login(username=self.tutorProfile.user.username, password=TEST_PASSWORD)
        testParams = self.TestParamsQuestionAnswer("answerQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        self.questionAnswer.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.questionAnswer.answer, testParams.answer)
        self.assertEquals(ajaxResponse["statusCode"], 200)

    def testAnswerQuestionAnswerObjectNotFound(self):
        testParams = self.TestParamsQuestionAnswer("answerQuestionAnswer", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this question has been deleted!")

    def testAnswerQuestionAnswerInvalidAnswerer(self):
        testParams = self.TestParamsQuestionAnswer("answerQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 403)
        self.assertEquals(ajaxResponse["statusCode"], 403)
        self.assertEquals(ajaxResponse["message"], "You are not allowed to answer this question. Only the tutor can answer it.")

    def testDeleteQuestionAnswerSuccess(self):
        testParams = self.TestParamsQuestionAnswer("deleteQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertFalse(QuestionAnswer.objects.filter(id=self.questionAnswer.id).exists())

    def testUpdateQuestionObjectNotFound(self):
        testParams = self.TestParamsQuestionAnswer("updateQuestion", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this question has been deleted!")

    def testUpdateQuestionSuccess(self):
        testParams = self.TestParamsQuestionAnswer("updateQuestion", self.questionAnswer.id)
        testParams.subject = "Maths"
        testParams.question = "Different Question"

        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        self.questionAnswer.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.questionAnswer.subject, testParams.subject)
        self.assertEquals(self.questionAnswer.question, testParams.question)
        self.assertEquals(ajaxResponse["statusCode"], 200)

    def testLikeQuestionAnswerObjectNotFound(self):
        testParams = self.TestParamsQuestionAnswer("likeQuestionAnswer", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this question has been deleted!")

    def testLikeQuestionAnswerLike(self):
        # L(0) : D(0) --> L(1) : D(0)
        testParams = self.TestParamsQuestionAnswer("likeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 1)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertTrue(self.user in self.questionAnswer.likes.all())
        self.assertFalse(self.user in self.questionAnswer.dislikes.all())

    def testLikeQuestionAnswerUnLike(self):
        # L(1) : D(0) --> L(0) : D(0)
        self.questionAnswer.likes.add(self.user)
        testParams = self.TestParamsQuestionAnswer("likeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertFalse(self.user in self.questionAnswer.likes.all())
        self.assertFalse(self.user in self.questionAnswer.dislikes.all())

    def testLikeQuestionAnswerDislikeToLike(self):
        # L(0) : D(1) --> L(1) : D(0)
        self.questionAnswer.dislikes.add(self.user)
        testParams = self.TestParamsQuestionAnswer("likeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 1)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertTrue(self.user in self.questionAnswer.likes.all())
        self.assertFalse(self.user in self.questionAnswer.dislikes.all())

    def testDislikeQuestionAnswerObjectNotFound(self):
        testParams = self.TestParamsQuestionAnswer("dislikeQuestionAnswer", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this question has been deleted!")

    def testDislikeQuestionAnswerDisLike(self):
        # L(0) : D(0) --> L(0) : D(1)
        testParams = self.TestParamsQuestionAnswer("dislikeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 1)
        self.assertFalse(self.user in self.questionAnswer.likes.all())
        self.assertTrue(self.user in self.questionAnswer.dislikes.all())

    def testDislikeQuestionAnswerUnDislike(self):
        # L(0) : D(1) --> L(0) : D(0)
        self.questionAnswer.dislikes.add(self.user)
        testParams = self.TestParamsQuestionAnswer("dislikeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertFalse(self.user in self.questionAnswer.likes.all())
        self.assertFalse(self.user in self.questionAnswer.dislikes.all())

    def testDislikeQuestionAnswerLikeToDislike(self):
        # L(1) : D(0) --> L(0) : D(1)
        self.questionAnswer.likes.add(self.user)
        testParams = self.TestParamsQuestionAnswer("dislikeQuestionAnswer", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 1)
        self.assertFalse(self.user in self.questionAnswer.likes.all())
        self.assertTrue(self.user in self.questionAnswer.dislikes.all())

    def testCreateTutorReviewSuccess(self):
        testParams = self.TestParamsTutorReview("createTutorReview")
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        tutorReview = TutorReview.objects.last()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["id"], tutorReview.id)
        # self.assertEquals(ajaxResponse["createdDate"], self.user.get_full_name())
        self.assertEquals(tutorReview.tutor, self.tutorProfile.user)
        self.assertEquals(tutorReview.reviewer, self.user)
        self.assertEquals(tutorReview.comment, testParams.comment)
        self.assertEquals(tutorReview.rating, testParams.rating)

    def testUpdateTutorReviewObjectNotFound(self):
        testParams = self.TestParamsTutorReview("updateTutorReview", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this review has been deleted!")

    def testUpdateTutorReviewSuccess(self):
        testParams = self.TestParamsTutorReview("updateTutorReview", self.questionAnswer.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)
        self.tutorReview.refresh_from_db()

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.tutorReview.comment, testParams.comment)
        self.assertEquals(ajaxResponse["statusCode"], 200)

    def testDeleteTutorReviewSuccess(self):
        testParams = self.TestParamsTutorReview("deleteTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertFalse(TutorReview.objects.filter(id=self.tutorReview.id).exists())

    def testLikeTutorReviewObjectNotFound(self):
        testParams = self.TestParamsTutorReview("likeTutorReview", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this review has been deleted!")

    def testLikeTutorReviewLike(self):
        # L(0) : D(0) --> L(1) : D(0)
        testParams = self.TestParamsTutorReview("likeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 1)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertTrue(self.user in self.tutorReview.likes.all())
        self.assertFalse(self.user in self.tutorReview.dislikes.all())

    def testLikeTutorReviewUnLike(self):
        # L(1) : D(0) --> L(0) : D(0)
        self.tutorReview.likes.add(self.user)
        testParams = self.TestParamsTutorReview("likeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertFalse(self.user in self.tutorReview.likes.all())
        self.assertFalse(self.user in self.tutorReview.dislikes.all())

    def testLikeTutorReviewDislikeToLike(self):
        # L(0) : D(1) --> L(1) : D(0)
        self.tutorReview.dislikes.add(self.user)
        testParams = self.TestParamsTutorReview("likeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 1)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertTrue(self.user in self.tutorReview.likes.all())
        self.assertFalse(self.user in self.tutorReview.dislikes.all())

    def testDislikeTutorReviewObjectNotFound(self):
        testParams = self.TestParamsTutorReview("dislikeTutorReview", 1000)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 404)
        self.assertEquals(ajaxResponse["statusCode"], 404)
        self.assertEquals(ajaxResponse["message"], "We think this review has been deleted!")

    def testDislikeTutorReviewDisLike(self):
        # L(0) : D(0) --> L(0) : D(1)
        testParams = self.TestParamsTutorReview("dislikeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 1)
        self.assertFalse(self.user in self.tutorReview.likes.all())
        self.assertTrue(self.user in self.tutorReview.dislikes.all())

    def testDislikeTutorReviewUnDislike(self):
        # L(0) : D(1) --> L(0) : D(0)
        self.tutorReview.dislikes.add(self.user)
        testParams = self.TestParamsTutorReview("dislikeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 0)
        self.assertFalse(self.user in self.tutorReview.likes.all())
        self.assertFalse(self.user in self.tutorReview.dislikes.all())

    def testDislikeTutorReviewLikeToDisLike(self):
        # L(1) : D(0) --> L(0) : D(1)
        self.tutorReview.likes.add(self.user)
        testParams = self.TestParamsTutorReview("dislikeTutorReview", self.tutorReview.id)
        response = self.get(testParams.getData())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertEquals(ajaxResponse["likeCount"], 0)
        self.assertEquals(ajaxResponse["dislikeCount"], 1)
        self.assertFalse(self.user in self.tutorReview.likes.all())
        self.assertTrue(self.user in self.tutorReview.dislikes.all())

    class TestParamsQuestionAnswer:

        def __init__(self, functionality, id=None):
            self.functionality = functionality
            self.subject = "English"
            self.question = "Question"
            self.answer = "Answer"
            self.id = id

        def getData(self):
            data = {
                'functionality': self.functionality,
                'subject': self.subject,
                'question': self.question,
                'answer': self.answer,
            }

            if self.id is not None:
                data['id'] = self.id
            return data

    class TestParamsTutorReview:

        def __init__(self, functionality, id=None):
            self.functionality = functionality
            self.rating = 3
            self.comment = "updated comment"
            self.id = id

        def getData(self):
            data = {
                'functionality': self.functionality,
                'rating': self.rating,
                'comment': self.comment,
            }

            if self.id is not None:
                data['id'] = self.id
            return data
