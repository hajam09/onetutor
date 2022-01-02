import operator
from functools import reduce
from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from accounts.models import Subject
from accounts.models import TutorProfile
from onetutor.operations import dateOperations
from onetutor.operations import generalOperations
from onetutor.operations import tutorOperations
from tutoring.models import ComponentGroup
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview


def mainpage(request):

	if request.method == "POST" and request.POST["generalQuery"]:
		return redirect("tutoring:searchBySubjectAndFilter", searchParameters=request.POST["generalQuery"])

	context = {
		"defaultPriceValues": {"priceFrom": 0, "priceTo": 100},
		"defaultScoreValues": {"scoreFrom": 0, "scoreTo": 2000},
		"showResult": False,
	}
	return render(request, 'tutoring/mainpage.html', context)


def searchBySubjectAndFilter(request, searchParameters=""):

	if request.method == "POST" and request.POST["generalQuery"]:
		return redirect("tutoring:searchBySubjectAndFilter", searchParameters=request.POST["generalQuery"])

	searchParametersSplit = searchParameters.split("/")
	subject = searchParametersSplit[0].lower().split(" ")

	try:
		filters = searchParametersSplit[1]
	except IndexError:
		filters = None

	hourlyMinimumRate = 0
	hourlyMaximumRate = 100
	minimumScore = 0
	maximumScore = 2000
	tickedTutorFeature = []

	if "and" in subject:
		requiredOperator = operator.and_
		subject = list(filter("and".__ne__, subject))
	else:
		requiredOperator = operator.or_

	query = reduce(requiredOperator, (Q(subjects__icontains=s) for s in subject))
	tutorList = TutorProfile.objects.filter(query).select_related('user').prefetch_related('tutorLessons', 'user__tutorReviews', 'components__componentGroup')
	if filters is not None:
		for f in filters.split("&"):
			r = f.split(":")

			if r[0] == "tutorFeature":
				tickedTutorFeature = f.split(":")[1].split(",")
				tutorList = set([ t
					   for t in tutorList
					   for c in t.components.all()
					   if c.code in tickedTutorFeature ])

			if r[0] == "hourlyPrice":
				hourlyMinimumRate = int(f.split(":")[1].split(",")[0])
				hourlyMaximumRate = int(f.split(":")[1].split(",")[1])
				tutorList = set([
					t for t in tutorList
					if hourlyMinimumRate <= t.chargeRate <= hourlyMaximumRate
				])

			if r[0] == "tutorScore":
				minimumScore = int(f.split(":")[1].split(",")[0])
				maximumScore = int(f.split(":")[1].split(",")[1])
				tutorList = set([
					t for t in tutorList
					if minimumScore <= sum([p.points for p in t.tutorLessons.all()]) <= maximumScore
				])

	if len(tutorList) == 0:
		messages.error(
			request,
			"Sorry, we couldn't find you a tutor for your search. Try entering something broad."
		)

	# only doing this because list to queryset is not possible and queryset is needed for Paginator.
	finalResultIds = [ t.id for t in tutorList]
	tutorList = TutorProfile.objects.filter(id__in=finalResultIds).select_related('user').prefetch_related('tutorLessons', 'user__tutorReviews', 'components__componentGroup')

	page = request.GET.get('page', 1)
	paginator = Paginator(tutorList, 15)

	try:
		tutorList = paginator.page(page)
	except PageNotAnInteger:
		tutorList = paginator.page(1)
	except EmptyPage:
		tutorList = paginator.page(paginator.num_pages)

	requiredComponentGroup = ComponentGroup.objects.filter(code__in=['TUTOR_FEATURE', 'EDUCATION_LEVEL', 'QUALIFICATION']).prefetch_related("components")

	context = {
		"generalQuery": searchParametersSplit[0],
		"tutorList": tutorList,
		"defaultPriceValues": {"priceFrom": hourlyMinimumRate, "priceTo": hourlyMaximumRate},
		"defaultScoreValues": {"scoreFrom": minimumScore, "scoreTo": maximumScore},
		"tickedTutorFeature": tickedTutorFeature,
		"tutorFeatureGroupComponent": next(i for i in requiredComponentGroup if i.code=='TUTOR_FEATURE'),
		"educationLevelComponent": next(i for i in requiredComponentGroup if i.code=='EDUCATION_LEVEL'),
		"qualificationComponent": next(i for i in requiredComponentGroup if i.code=='QUALIFICATION'),
		"showResult": True,
	}
	return render(request, 'tutoring/mainpage.html', context)


def viewTutorProfile(request, tutorProfileKey):

	try:
		tutorProfile = TutorProfile.objects.get(secondaryKey=tutorProfileKey)
	except TutorProfile.DoesNotExist:
		return redirect("tutoring:mainpage")

	tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")

	if request.is_ajax():
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
			return JsonResponse(response)

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
				return JsonResponse(response)

			if questionAnswer.answerer != request.user:
				response = {
					"statusCode": HTTPStatus.FORBIDDEN,
					"message": 'You are not allowed to answer this question. Only the tutor can answer it.'
				}
				return JsonResponse(response)

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
			return JsonResponse(response)

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
				return JsonResponse(response)

			questionAnswer.subject = subject
			questionAnswer.question = question
			questionAnswer.save(update_fields=['subject', 'question'])

			response = {
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "likeQuestionAnswer":

			id = request.GET.get('id', None)

			try:
				thisComment = QuestionAnswer.objects.get(pk=id)
			except QuestionAnswer.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'We think this question has been deleted!'
				}
				return JsonResponse(response)

			thisComment.like(request)

			response = {
				"likeCount": thisComment.likes.count(),
				"dislikeCount": thisComment.dislikes.count(),
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "dislikeQuestionAnswer":

			id = request.GET.get('id', None)

			try:
				thisComment = QuestionAnswer.objects.get(id=id)
			except QuestionAnswer.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'We think this question has been deleted!'
				}
				return JsonResponse(response)

			thisComment.dislike(request)

			response = {
				"likeCount": thisComment.likes.count(),
				"dislikeCount": thisComment.dislikes.count(),
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

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
			return JsonResponse(response)

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
				return JsonResponse(response)

			tutorReview.comment = comment
			tutorReview.save()

			response = {
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "deleteTutorReview":

			id = request.GET.get('id', None)
			TutorReview.objects.filter(pk=id).delete()

			response = {
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "likeTutorReview":

			id = request.GET.get('id', None)

			try:
				tutorReview = TutorReview.objects.get(id=id)
			except TutorReview.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'We think this review has been deleted!'
				}
				return JsonResponse(response)

			tutorReview.like(request)

			response = {
				"likeCount": tutorReview.likes.count(),
				"dislikeCount": tutorReview.dislikes.count(),
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "dislikeTutorReview":

			id = request.GET.get('id', None)

			try:
				tutorReview = TutorReview.objects.get(id=id)
			except TutorReview.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'We think this review has been deleted!'
				}
				return JsonResponse(response)

			tutorReview.dislike(request)

			response = {
				"likeCount": tutorReview.likes.count(),
				"dislikeCount": tutorReview.dislikes.count(),
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		raise Exception("Unknown functionality in viewTutorProfile")

	context = {
		"tutorProfile": tutorProfile,
		"subjects": Subject.objects.all(),
		"questionAndAnswers": QuestionAnswer.objects.filter(answerer=tutorProfile.user).select_related('questioner', 'answerer').prefetch_related('likes', 'dislikes').order_by('-id'),
		"tutorReviews": TutorReview.objects.filter(tutor=tutorProfile.user).order_by('date').select_related('reviewer').prefetch_related('likes', 'dislikes').order_by('-date'),
	}

	return render(request, "tutoring/tutorprofile.html", context)

@login_required
def tutorsQuestions(request):

	try:
		tutorProfile = TutorProfile.objects.get(user=request.user)
	except TutorProfile.DoesNotExist:
		return redirect("accounts:select-profile")

	if request.is_ajax():
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

	allQuestionAnswers = QuestionAnswer.objects.filter(answerer=tutorProfile.user).select_related('questioner', 'answerer').prefetch_related('likes', 'dislikes').order_by('-id')
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

def viewstudentprofile(request, studentId):
	print("bb")
	return render(request, "tutoring/studentprofile.html", {})


def questionAnswerThread(request, questionId):

	questionAnswer = QuestionAnswer.objects.select_related('questioner').get(id=questionId)

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "createQuestionAnswerComment":
			comment = request.GET.get('comment', None)

			questionAnswerComment = QuestionAnswerComment.objects.create(
				questionAnswer=questionAnswer,
				creator=request.user,
				comment=comment
			)

			newComment = {
				'id': questionAnswerComment.id,
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
			return JsonResponse(response)

		elif functionality == "deleteQuestionAnswerComment":
			id = request.GET.get('id', None)

			QuestionAnswerComment.objects.filter(pk=int(id)).delete()

			response = {
				"statusCode": HTTPStatus.OK,
			}
			return JsonResponse(response)

		elif functionality == "updateQuestionAnswerComment":
			id = request.GET.get('id', None)
			comment = request.GET.get('comment', None)

			try:
				questionAnswerComment = QuestionAnswerComment.objects.get(id=int(id))
			except QuestionAnswerComment.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'Error updating your comment. Please try again later!'
				}
				return JsonResponse(response)

			questionAnswerComment.comment = comment
			questionAnswerComment.edited = True
			questionAnswerComment.save(update_fields=['comment', 'edited'])

			updatedComment = {
				'id': questionAnswerComment.id,
				'comment': questionAnswerComment.comment.replace("\n", "<br />"),
				'edited': True,
			}

			response = {
				"statusCode": HTTPStatus.OK,
				"updatedComment": updatedComment,
			}
			return JsonResponse(response)

		elif functionality == "likeQuestionAnswerComment" or functionality == "dislikeQuestionAnswerComment":
			id = request.GET.get('id', None)

			try:
				questionAnswerComment = QuestionAnswerComment.objects.get(id=int(id))
			except QuestionAnswerComment.DoesNotExist:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": 'Error occurred. Please try again later!'
				}
				return JsonResponse(response)

			if functionality == "likeQuestionAnswerComment":
				questionAnswerComment.like(request)
			else:
				questionAnswerComment.dislike(request)

			response = {
				"statusCode": HTTPStatus.OK,
				"likeCount": questionAnswerComment.likes.count(),
				"dislikeCount": questionAnswerComment.dislikes.count(),
			}
			return JsonResponse(response)

		raise Exception("Unknown functionality questionAnswerThread view")

	allQuestionAnswerComment = QuestionAnswerComment.objects.filter(questionAnswer=questionAnswer).select_related('creator').prefetch_related('likes', 'dislikes').order_by('-id')
	page = request.GET.get('page', 1)
	paginator = Paginator(allQuestionAnswerComment, 15)

	try:
		questionAnswerComment = paginator.page(page)
	except PageNotAnInteger:
		questionAnswerComment = paginator.page(1)
	except EmptyPage:
		questionAnswerComment = paginator.page(paginator.num_pages)

	context = {
		"questionAnswer": questionAnswer,
		"questionAnswerComment": questionAnswerComment
	}
	return render(request, "tutoring/questionAnswerThread.html", context)