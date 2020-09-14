import operator
from functools import reduce
from http import HTTPStatus

from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from accounts.models import TutorProfile, Education
from onetutor.operations import dateOperations, generalOperations
from tutoring.models import Component, Availability
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview

TUTOR_FEATURE = ["inPersonLessons", "onlineLessons", "pro", "dbs", "sc"]
QUALIFICATION = ["higherSecondary", "foundationDegree", "bachelorDegree", "masterDegree", "doctorate"]
EDUCATION_LEVEL = ["SATS", "GCSE", "ASLEVEL", "ALEVEL", "UNDERGRADUATE", "POSTGRADUATE"]
QUALIFICATION_MAP = {
    "higherSecondary": "Higher Secondary",
    "foundationDegree": "Foundation Degree",
    "bachelorDegree": "Bachelor Degree",
    "masterDegree": "Master Degree",
    "doctorate": "Doctorate Degree",
}


class TutorQuery:

    def __init__(self, request):
        self.subject = request.GET.get("subject")
        self.sortBy = request.GET.get("sortBy")
        self.rating = int(request.GET.get("rating", -1))
        self.minimumScore = int(request.GET.get("minimumScore", 0))
        self.maximumScore = int(request.GET.get("maximumScore", 9999999999))
        self.qualification = request.GET.get("qualification", [])
        self.tutorFeature = request.GET.get("tutorFeature", [])
        self.minimumRate = round(float(request.GET.get("minimumRate", 0.0)), 2)
        self.maximumRate = round(float(request.GET.get("maximumRate", 9999999999.99)), 2)
        self.myEducationLevel = request.GET.get("myEducationLevel", EDUCATION_LEVEL)
        self.page = request.GET.get("page", 1)

        if self.qualification:
            self.qualification = [QUALIFICATION_MAP[i] for i in self.qualification.split(",")]

        if self.tutorFeature:
            self.tutorFeature = self.tutorFeature.split(",")

        if isinstance(self.myEducationLevel, str):
            self.myEducationLevel = self.myEducationLevel.split(",")


class TutorProfileSerializer:

    def __init__(self, request, querySet, many=False):
        self.request = request
        self.querySet = querySet
        self.many = many

    def serialize(self, tutor):
        reviews = tutor.user.tutorReviews
        lessons = tutor.tutorLessons
        return {
            "id": tutor.id,
            "url": tutor.url,
            "user": generalOperations.userSerializer(tutor.user),
            "summary": tutor.summary,
            "about": tutor.about,
            "chargeRate": tutor.chargeRate,
            "features": [
                {
                    "id": feature.id,
                    "internalKey": feature.internalKey,
                    "colour": feature.colour,
                }
                for feature in tutor.features.all()
            ],
            "reviews": {
                "count": reviews.count(),
                "average": round(sum([review.rating for review in reviews.all()]) / reviews.count(), 2)
            },
            "lessons": {
                "count": lessons.count(),
                "points": sum([lesson.points for lesson in lessons.all()])
            }
        }

    def data(self):
        serializeItems = []
        query = TutorQuery(self.request)

        for tutor in self.querySet:
            tutorSerialized = self.serialize(tutor)

            ratingCriteria = tutorSerialized.get("reviews").get("average") > query.rating
            scoreCriteria = query.minimumScore <= tutorSerialized.get("lessons").get("points") <= query.maximumScore
            qualificationCriteria = True if not query.qualification else any(
                x in query.qualification for x in [i.qualification for i in tutor.user.education.all()]
            )

            criteriaMet = ratingCriteria and scoreCriteria and qualificationCriteria
            if criteriaMet:
                serializeItems.append(tutorSerialized)
        return serializeItems if self.many else serializeItems[0]


@method_decorator(csrf_exempt, name='dispatch')
class TutorListingApiEventVersion1Component(View):
    def get(self, *args, **kwargs):
        tq = TutorQuery(self.request)

        # Choosing and operator for subject is too restrictive at the moment.
        subjectQuery = reduce(operator.or_, (Q(subjects__icontains=i) for i in tq.subject.split()))
        featureQuery = reduce(operator.or_, (Q(features__code__icontains=i) for i in tq.tutorFeature or TUTOR_FEATURE))
        priceQuery = reduce(operator.and_, (Q(chargeRate__gte=tq.minimumRate), Q(chargeRate__lte=tq.maximumRate)))
        teachingLevelQuery = reduce(operator.or_, (Q(teachingLevels__code__icontains=i) for i in tq.myEducationLevel or EDUCATION_LEVEL))

        tutorList = TutorProfile.objects.filter(
            subjectQuery & featureQuery & priceQuery & teachingLevelQuery
        ).select_related("user").prefetch_related(
            "features", "user__tutorReviews", "tutorLessons", "user__education"
        ).distinct()

        paginator = Paginator(tutorList, 10)
        try:
            tutorList = paginator.page(tq.page)
        except PageNotAnInteger:
            tutorList = paginator.page(1)
        except EmptyPage:
            tutorList = paginator.page(paginator.num_pages)

        tutorProfileSerializer = TutorProfileSerializer(self.request, tutorList, many=True)

        response = {
            "success": True,
            "data": {
                "tutors": tutorProfileSerializer.data(),
                "pagination": {
                    "currentPage": tutorList.number,
                    "hasOtherPages": tutorList.has_other_pages(),
                    "hasPrevious": tutorList.has_previous(),
                    "hasNext": tutorList.has_next(),
                    "previousPageNumber": tutorList.previous_page_number() if tutorList.has_previous() else None,
                    "nextPageNumber": tutorList.next_page_number() if tutorList.has_next() else None,
                    "paginator": [
                        {
                            "pageNumber": i,
                            "isActive": i == tutorList.number
                        }
                        for i in tutorList.paginator.page_range
                    ]
                },
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class EducationObjectApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        educations = [
            {
                "id": e.id,
                "schoolName": e.schoolName,
                "qualification": e.qualification,
                "startDate": e.startDate.strftime("%b %d, %Y"),
                "endDate": e.endDate.strftime("%b %d, %Y"),
            }
            for e in Education.objects.filter(**self.request.GET.dict())
        ]
        response = {
            "success": True,
            "data": {
                "educations": educations,
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class AvailabilityObjectApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        response = {
            "success": True,
            "data": {
                "availability": Availability.objects.get(**self.request.GET.dict()).getAvailability(),
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)


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


@method_decorator(csrf_exempt, name='dispatch')
class ComponentObjectsApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        componentGroupCode = self.request.GET.get('componentGroupCode')
        components = Component.objects.filter(componentGroup__code=componentGroupCode)
        response = {
            "success": True,
            "data": {
                "components": [
                    {
                        "id": component.id,
                        "internalKey": component.internalKey,
                        "reference": component.reference,
                        "languageKey": component.languageKey,
                        "code": component.code,
                        "icon": component.icon,
                        "deleteFl": component.deleteFl,
                        "colour": component.colour,
                        "orderNo": component.orderNo,
                        "versionNo": component.versionNo,

                    }
                    for component in components
                ]
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)
