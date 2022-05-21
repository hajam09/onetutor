from http import HTTPStatus

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from accounts.models import TutorProfile
from onetutor.operations import dateOperations
from tutoring.models import QuestionAnswer, TutorReview, QuestionAnswerComment


@method_decorator(csrf_exempt, name='dispatch')
class QuestionAnswerObjectApiEventVersion1Component(View):

    def delete(self, *args, **kwargs):
        # deleteQuestionAnswer
        id = self.kwargs.get("id", None)

        QuestionAnswer.objects.filter(pk=id).delete()
        response = {
            "success": True,
            "message": "Deleted successfully."
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def get(self, *args, **kwargs):
        id = self.kwargs.get("id", None)

        try:
            questionAnswer = QuestionAnswer.objects.get(id=id)
        except QuestionAnswer.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        response = {
            "success": True,
            "data": {
                "id": questionAnswer.id,
                "subject": questionAnswer.subject,
                "question": questionAnswer.question,
                "answer": questionAnswer.answer,
                "questioner": {
                    "id": questionAnswer.questioner.id,
                    "firstName": questionAnswer.questioner.first_name,
                    "lastName": questionAnswer.questioner.last_name
                },
                "answerer": {
                    "id": questionAnswer.answerer.id,
                    "firstName": questionAnswer.answerer.first_name,
                    "lastName": questionAnswer.answerer.last_name
                },
                "likes": {
                    "count": questionAnswer.likes.count()
                },
                "dislikes": {
                    "count": questionAnswer.dislikes.count()
                },
                "date": dateOperations.humanizePythonDate(questionAnswer.date)
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def put(self, *args, **kwargs):
        # answerQuestionAnswer, updateQuestion
        id = self.kwargs.get("id", None)
        question = self.request.GET.get('question', None)
        answer = self.request.GET.get('answer', None)
        subject = self.request.GET.get('subject', None)

        try:
            questionAnswer = QuestionAnswer.objects.get(pk=id)
        except QuestionAnswer.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        updateFields = []
        if question is not None:
            questionAnswer.question = question
            updateFields.append("question")

        if answer is not None:
            questionAnswer.answer = answer
            updateFields.append("answer")

        if subject is not None:
            questionAnswer.subject = subject
            updateFields.append("subject")

        questionAnswer.save(update_fields=updateFields)
        response = {
            "success": True,
            "message": "Update is successful."
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def post(self, *args, **kwargs):
        # postQuestionAnswer
        subject = self.request.GET.get('subject', None)
        question = self.request.GET.get('question', None)
        tutorId = self.request.GET.get('tutorId', None)

        try:
            tutorProfile = TutorProfile.objects.get(id=tutorId)
        except TutorProfile.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a tutor with id " + str(tutorId)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        questionAnswer = QuestionAnswer.objects.create(
            subject=subject,
            question=question,
            questioner=self.request.user,
            answerer=tutorProfile.user
        )

        response = {
            "success": True,
            "data": {
                "id": questionAnswer.id,
                "subject": questionAnswer.subject,
                "question": questionAnswer.question,
                "answer": questionAnswer.answer,
                "questioner": {
                    "id": questionAnswer.questioner.id,
                    "firstName": questionAnswer.questioner.first_name,
                    "lastName": questionAnswer.questioner.last_name
                },
                "answerer": {
                    "id": questionAnswer.answerer.id,
                    "firstName": questionAnswer.answerer.first_name,
                    "lastName": questionAnswer.answerer.last_name
                },
                "likes": {
                    "count": questionAnswer.likes.count()
                },
                "dislikes": {
                    "count": questionAnswer.dislikes.count()
                },
                "createdDate": dateOperations.humanizePythonDate(questionAnswer.date)
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class QuestionAnswerObjectLikeOrDislikeApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        # likeQuestionAnswer -> like, dislikeQuestionAnswer -> dislike
        id = self.kwargs.get("id", None)
        action = self.kwargs.get("action", None)

        try:
            questionAnswer = QuestionAnswer.objects.get(pk=id)
        except QuestionAnswer.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        if action is None:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        if action == "like":
            questionAnswer.like(self.request)
        elif action == "dislike":
            questionAnswer.dislike(self.request)
        else:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        response = {
            "success": True,
            "id": id,
            "likeCount": questionAnswer.likes.count(),
            "dislikeCount": questionAnswer.dislikes.count(),
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class TutorReviewObjectApiEventVersion1Component(View):

    def delete(self, *args, **kwargs):
        # deleteTutorReview
        id = self.kwargs.get("id", None)

        TutorReview.objects.filter(pk=id).delete()
        response = {
            "success": True,
            "message": "Deleted successfully."
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def get(self, *args, **kwargs):
        id = self.kwargs.get("id", None)

        try:
            tutorReview = TutorReview.objects.get(id=id)
        except TutorReview.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        response = {
            "success": True,
            "data": {
                "id": tutorReview.id,
                "tutor": {
                    "id": tutorReview.tutor.id,
                    "firstName": tutorReview.tutor.first_name,
                    "lastName": tutorReview.tutor.last_name,
                },
                "reviewer": {
                    "id": tutorReview.reviewer.id,
                    "firstName": tutorReview.reviewer.first_name,
                    "lastName": tutorReview.reviewer.last_name,
                },
                "comment": tutorReview.comment,
                "rating": tutorReview.rating,
                "likes": {
                    "count": tutorReview.likes.count()
                },
                "dislikes": {
                    "count": tutorReview.dislikes.count()
                },
                "createdDate": dateOperations.humanizePythonDate(tutorReview.date),
                "edited": tutorReview.edited
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def put(self, *args, **kwargs):
        # updateTutorReview
        id = self.kwargs.get("id", None)
        comment = self.request.GET.get('comment', None)

        try:
            tutorReview = TutorReview.objects.get(id=id)
        except TutorReview.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        updateFields = []
        if comment is not None:
            tutorReview.question = comment
            updateFields.append("comment")

        tutorReview.save(update_fields=updateFields)
        response = {
            "success": True,
            "message": "Update is successful."
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def post(self, *args, **kwargs):
        # createTutorReview
        rating = self.request.GET.get('rating', None)
        comment = self.request.GET.get('comment', None)
        tutorId = self.request.GET.get('tutorId', None)

        try:
            tutorProfile = TutorProfile.objects.get(id=tutorId)
        except TutorProfile.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a tutor with id " + str(tutorId)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        tutorReview = TutorReview.objects.create(
            tutor=tutorProfile.user,
            reviewer=self.request.user,
            comment=comment,
            rating=rating,
        )

        response = {
            "success": True,
            "data": {
                "id": tutorReview.id,
                "tutor": {
                    "id": tutorReview.tutor.id,
                    "firstName": tutorReview.tutor.first_name,
                    "lastName": tutorReview.tutor.last_name,
                },
                "reviewer": {
                    "id": tutorReview.reviewer.id,
                    "firstName": tutorReview.reviewer.first_name,
                    "lastName": tutorReview.reviewer.last_name,
                },
                "comment": tutorReview.comment,
                "rating": tutorReview.rating,
                "likes": {
                    "count": tutorReview.likes.count()
                },
                "dislikes": {
                    "count": tutorReview.dislikes.count()
                },
                "createdDate": dateOperations.humanizePythonDate(tutorReview.date),
                "edited": tutorReview.edited
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class TutorReviewObjectLikeOrDislikeApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        # likeTutorReview -> like, dislikeTutorReview -> dislike
        id = self.kwargs.get("id", None)
        action = self.kwargs.get("action", None)

        try:
            tutorReview = TutorReview.objects.get(pk=id)
        except TutorReview.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        if action is None:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        if action == "like":
            tutorReview.like(self.request)
        elif action == "dislike":
            tutorReview.dislike(self.request)
        else:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        response = {
            "success": True,
            "id": id,
            "likeCount": tutorReview.likes.count(),
            "dislikeCount": tutorReview.dislikes.count(),
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class QuestionAnswerCommentObjectApiEventVersion1Component(View):

    def delete(self, *args, **kwargs):
        # deleteQuestionAnswerComment
        id = self.kwargs.get("id", None)

        QuestionAnswerComment.objects.filter(pk=id).delete()
        response = {
            "success": True,
            "message": "Deleted successfully."
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def get(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        # updateQuestionAnswerComment
        id = self.kwargs.get("id", None)
        comment = self.request.GET.get('comment', None)

        try:
            questionAnswerComment = QuestionAnswerComment.objects.get(id=id)
        except QuestionAnswerComment.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        questionAnswerComment.comment = comment
        questionAnswerComment.edited = True
        questionAnswerComment.save(update_fields=['comment', 'edited'])

        response = {
            "success": True,
            "message": "Update is successful.",
            "data": {
                "id": questionAnswerComment.id,
                "creator": {
                    "id": questionAnswerComment.creator.id,
                    "firstName": questionAnswerComment.creator.first_name,
                    "lastName": questionAnswerComment.creator.last_name,
                },
                "likes": {
                    "count": questionAnswerComment.likes.count()
                },
                "dislikes": {
                    "count": questionAnswerComment.dislikes.count()
                },
                "comment": questionAnswerComment.comment.replace("\n", "<br />"),
                "date": dateOperations.humanizePythonDate(questionAnswerComment.date),
                "edited": True,
                "canEdit": True
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def post(self, *args, **kwargs):
        # createQuestionAnswerComment
        id = self.kwargs.get("id", None)
        comment = self.request.GET.get('comment', None)

        try:
            questionAnswer = QuestionAnswer.objects.get(id=id)
        except QuestionAnswer.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        questionAnswerComment = QuestionAnswerComment.objects.create(
            questionAnswer=questionAnswer,
            creator=self.request.user,
            comment=comment
        )

        response = {
            "success": True,
            "data": {
                "id": questionAnswerComment.id,
                "creator": {
                    "id": questionAnswerComment.creator.id,
                    "firstName": questionAnswerComment.creator.first_name,
                    "lastName": questionAnswerComment.creator.last_name,
                },
                "likes": {
                    "count": questionAnswerComment.likes.count()
                },
                "dislikes": {
                    "count": questionAnswerComment.dislikes.count()
                },
                "comment": questionAnswerComment.comment.replace("\n", "<br />"),
                "date": dateOperations.humanizePythonDate(questionAnswerComment.date),
                "edited": False,
                "canEdit": True
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class QuestionAnswerCommentObjectLikeOrDislikeApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        # likeQuestionAnswerComment -> like, dislikeQuestionAnswerComment -> dislike
        id = self.kwargs.get("id", None)
        action = self.kwargs.get("action", None)

        try:
            questionAnswerComment = QuestionAnswerComment.objects.get(pk=id)
        except QuestionAnswerComment.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find an object."
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        if action is None:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        if action == "like":
            questionAnswerComment.like(self.request)
        elif action == "dislike":
            questionAnswerComment.dislike(self.request)
        else:
            response = {
                "success": False,
                "message": "Could not perform this action"
            }
            return JsonResponse(response, status=HTTPStatus.METHOD_NOT_ALLOWED)

        response = {
            "success": True,
            "id": id,
            "likeCount": questionAnswerComment.likes.count(),
            "dislikeCount": questionAnswerComment.dislikes.count(),
        }
        return JsonResponse(response, status=HTTPStatus.OK)
