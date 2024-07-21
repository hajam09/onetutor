import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

# from accounts.models import Subject
from accounts.models import TutorProfile
from onetutor.operations import dateOperations
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview

# ---------------------------------------------------------------------- #


def indexView(request):
    return render(request, "tutoring/indexPage.html")


def tutorProfileView(request, url):
    try:
        tutorProfile = TutorProfile.objects.get(url=url)
    except TutorProfile.DoesNotExist:
        return redirect("tutoring:index-view")

    context = {
        "tutorProfile": tutorProfile,
    }
    return render(request, "tutoring/tutorProfilePage.html", context)


def viewTutorProfile(request, url):
    try:
        tutorProfile = TutorProfile.objects.get(url=url)
    except TutorProfile.DoesNotExist:
        return redirect("tutoring:index-view")

    tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        functionality = request.GET.get('functionality', None)

        if not request.user.is_authenticated:
            response = {
                'statusCode': HTTPStatus.UNAUTHORIZED
            }
            return JsonResponse(response)

        if functionality == "postQuestionAnswer":

            subject = request.GET.get('subject', None)
            question = request.GET.get('question', None)

            questionAnswer = QuestionAnswer.objects.create(
                subject=subject,
                question=question,
                questioner=request.user,
                answerer=tutorProfile.user
            )

            response = {
                'id': questionAnswer.id,
                'answer': questionAnswer.answer,
                'questionerFullName': questionAnswer.questioner.get_full_name(),
                'createdDate': dateOperations.humanizePythonDate(questionAnswer.date),
                'likeCount': 0,
                'dislikeCount': 0,
                'statusCode': HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "answerQuestionAnswer":

            id = request.GET.get('id', None)
            answer = request.GET.get('answer', None)

            try:
                questionAnswer = QuestionAnswer.objects.get(pk=id)
            except QuestionAnswer.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this question has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            if questionAnswer.answerer != request.user:
                response = {
                    "statusCode": HTTPStatus.FORBIDDEN,
                    "message": 'You are not allowed to answer this question. Only the tutor can answer it.'
                }
                return JsonResponse(response, status=HTTPStatus.FORBIDDEN)

            questionAnswer.answer = answer
            questionAnswer.save(update_fields=['answer'])
            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "deleteQuestionAnswer":

            id = request.GET.get('id', None)
            QuestionAnswer.objects.filter(pk=id).delete()
            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "updateQuestion":

            id = request.GET.get('id', None)
            subject = request.GET.get('subject', None)
            question = request.GET.get('question', None)

            try:
                questionAnswer = QuestionAnswer.objects.get(pk=id)
            except QuestionAnswer.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this question has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            questionAnswer.subject = subject
            questionAnswer.question = question
            questionAnswer.save(update_fields=['subject', 'question'])

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "likeQuestionAnswer":

            id = request.GET.get('id', None)

            try:
                thisComment = QuestionAnswer.objects.get(pk=id)
            except QuestionAnswer.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this question has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            thisComment.like(request)

            response = {
                "likeCount": thisComment.likes.count(),
                "dislikeCount": thisComment.dislikes.count(),
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "dislikeQuestionAnswer":

            id = request.GET.get('id', None)

            try:
                thisComment = QuestionAnswer.objects.get(id=id)
            except QuestionAnswer.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this question has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            thisComment.dislike(request)

            response = {
                "likeCount": thisComment.likes.count(),
                "dislikeCount": thisComment.dislikes.count(),
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "createTutorReview":

            rating = request.GET.get('rating', None)
            comment = request.GET.get('comment', None)

            tutorReview = TutorReview.objects.create(
                tutor=tutorProfile.user,
                reviewer=request.user,
                comment=comment,
                rating=rating,
            )

            response = {
                'id': tutorReview.id,
                'createdDate': dateOperations.humanizePythonDate(tutorReview.date),
                'statusCode': HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "updateTutorReview":

            id = request.GET.get('id', None)
            comment = request.GET.get('comment', None)

            try:
                tutorReview = TutorReview.objects.get(id=id)
            except TutorReview.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this review has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            tutorReview.comment = comment
            tutorReview.save()

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "deleteTutorReview":

            id = request.GET.get('id', None)
            TutorReview.objects.filter(pk=id).delete()

            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "likeTutorReview":

            id = request.GET.get('id', None)

            try:
                tutorReview = TutorReview.objects.get(id=id)
            except TutorReview.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this review has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            tutorReview.like(request)

            response = {
                "likeCount": tutorReview.likes.count(),
                "dislikeCount": tutorReview.dislikes.count(),
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "dislikeTutorReview":

            id = request.GET.get('id', None)

            try:
                tutorReview = TutorReview.objects.get(id=id)
            except TutorReview.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'We think this review has been deleted!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            tutorReview.dislike(request)

            response = {
                "likeCount": tutorReview.likes.count(),
                "dislikeCount": tutorReview.dislikes.count(),
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        raise Exception("Unknown functionality in viewTutorProfile")

    context = {
        "tutorProfile": tutorProfile,
        # "subjects": Subject.objects.all(),
        "questionAndAnswers": QuestionAnswer.objects.filter(answerer=tutorProfile.user).select_related('questioner',
                                                                                                       'answerer').prefetch_related(
            'likes', 'dislikes').order_by('-id'),
        "tutorReviews": TutorReview.objects.filter(tutor=tutorProfile.user).select_related('reviewer').prefetch_related(
            'likes', 'dislikes'),
    }
    return render(request, "tutoring/tutorprofile.html", context)


@login_required
def tutorsQuestions(request):
    tutorProfile = TutorProfile.objects.get(user=request.user)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        functionality = request.GET.get('functionality', None)

        if functionality == "deleteQuestionAnswer":
            id = request.GET.get('id', None)

            QuestionAnswer.objects.filter(pk=int(id)).delete()
            response = {
                "statusCode": HTTPStatus.OK
            }
            return JsonResponse(response)

        elif functionality == "updateQuestionAnswer":
            id = request.GET.get('id', None)
            answer = request.GET.get('answer', None)

            try:
                questionAnswer = QuestionAnswer.objects.get(pk=int(id))
            except QuestionAnswer.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Error updating the answer. Please try again later!'
                }
                return JsonResponse(response)

            questionAnswer.answer = answer
            questionAnswer.save(update_fields=['answer'])

            response = {
                "statusCode": HTTPStatus.OK,
                "answer": questionAnswer.answer.replace("\n", "<br />")
            }
            return JsonResponse(response)

        raise Exception("Unknown functionality tutorsQuestions view.")

    allQuestionAnswers = QuestionAnswer.objects.filter(answerer=tutorProfile.user).select_related('questioner',
                                                                                                  'answerer').prefetch_related(
        'likes', 'dislikes').order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(allQuestionAnswers, 15)

    try:
        questionAndAnswers = paginator.page(page)
    except PageNotAnInteger:
        questionAndAnswers = paginator.page(1)
    except EmptyPage:
        questionAndAnswers = paginator.page(paginator.num_pages)

    context = {
        "questionAndAnswers": questionAndAnswers
    }
    return render(request, "tutoring/tutorsQuestions.html", context)


def viewStudentProfile(request, url):
    """
    Student cannot change their profile picture.
    Only the current teaching tutor or any tutor who taught within last seven days can view the profile.
    Student or Parent can make the profile private.
    Student or Parent can allow specific users to view the profile or prevent them from viewing the profile.
    Parent can view the chat messages between their child and others.
    """
    return render(request, "tutoring/studentProfile.html")


def questionAnswerThread(request, questionId):
    questionAnswer = QuestionAnswer.objects.select_related('questioner').get(id=questionId)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        functionality = request.GET.get('functionality', None)

        if functionality == "createQuestionAnswerComment":
            comment = request.GET.get('comment', None)

            questionAnswerComment = QuestionAnswerComment.objects.create(
                questionAnswer=questionAnswer,
                creator=request.user,
                comment=comment
            )

            newComment = {
                'commentId': questionAnswerComment.id,
                'creatorFullName': questionAnswerComment.creator.get_full_name(),
                'comment': questionAnswerComment.comment.replace("\n", "<br />"),
                'date': dateOperations.humanizePythonDate(questionAnswerComment.date),
                'likeCount': 0,
                'dislikeCount': 0,
                'edited': False,
                'canEdit': True
            }

            response = {
                "statusCode": HTTPStatus.OK,
                "newComment": newComment,
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "deleteQuestionAnswerComment":
            commentId = request.GET.get('commentId', None)

            QuestionAnswerComment.objects.filter(pk=int(commentId)).delete()

            response = {
                "statusCode": HTTPStatus.OK,
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "updateQuestionAnswerComment":
            commentId = request.GET.get('commentId', None)
            comment = request.GET.get('comment', None)

            try:
                questionAnswerComment = QuestionAnswerComment.objects.get(id=int(commentId))
            except QuestionAnswerComment.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Error updating your comment. Please try again later!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            questionAnswerComment.comment = comment
            questionAnswerComment.edited = True
            questionAnswerComment.save(update_fields=['comment', 'edited'])

            updatedComment = {
                'commentId': questionAnswerComment.id,
                'comment': questionAnswerComment.comment.replace("\n", "<br />"),
                'edited': True,
            }

            response = {
                "statusCode": HTTPStatus.OK,
                "updatedComment": updatedComment,
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        elif functionality == "likeQuestionAnswerComment" or functionality == "dislikeQuestionAnswerComment":
            commentId = request.GET.get('commentId', None)

            try:
                questionAnswerComment = QuestionAnswerComment.objects.get(id=int(commentId))
            except QuestionAnswerComment.DoesNotExist:
                response = {
                    "statusCode": HTTPStatus.NOT_FOUND,
                    "message": 'Error occurred. Please try again later!'
                }
                return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

            if functionality == "likeQuestionAnswerComment":
                questionAnswerComment.like(request)
            else:
                questionAnswerComment.dislike(request)

            response = {
                "statusCode": HTTPStatus.OK,
                "likeCount": questionAnswerComment.likes.count(),
                "dislikeCount": questionAnswerComment.dislikes.count(),
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        raise Exception("Unknown functionality questionAnswerThread view")

    allQuestionAnswerComment = QuestionAnswerComment.objects.filter(questionAnswer=questionAnswer).select_related(
        'creator').prefetch_related('likes', 'dislikes').order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(allQuestionAnswerComment, 15)

    try:
        questionAnswerComment = paginator.page(page)
    except PageNotAnInteger:
        questionAnswerComment = paginator.page(1)
    except EmptyPage:
        questionAnswerComment = paginator.page(paginator.num_pages)

    questionAnswerCommentJson = [
        {
            'commentId': i.pk,
            'creatorFullName': i.creator.get_full_name(),
            'comment': i.comment.replace("\n", "<br />"),
            'date': dateOperations.humanizePythonDate(i.date),
            'likeCount': i.likes.count(),
            'dislikeCount': i.dislikes.count(),
            'canEdit': request.user == i.creator,
            'edited': i.edited,
            'show': True

        }
        for i in allQuestionAnswerComment
    ]

    context = {
        "questionAnswer": questionAnswer,
        "questionAnswerComment": questionAnswerComment,
        "questionAnswerCommentJson": json.dumps(questionAnswerCommentJson)
    }
    return render(request, "tutoring/questionAnswerThread.html", context)
