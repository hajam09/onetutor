from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from accounts.models import Subject
from accounts.models import TutorProfile
from onetutor.operations import dateOperations
from onetutor.operations import tutorOperations
from onetutor.operations import generalOperations
from tutoring.models import QuestionAnswer
from tutoring.models import ComponentGroup
from tutoring.models import Component
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview


def mainpage(request):

	if request.method == "POST" and request.POST["generalQuery"]:
		return redirect("tutoring:searchBySubjectAndFilter", searchParameters=request.POST["generalQuery"])

	context = {
		"defaultPriceValues": {"priceFrom": 0, "priceTo": 100},
		"defaultScoreValues": {"scoreFrom": 0, "scoreTo": 2000},
	}
	return render(request, 'tutoring/mainpage.html', context)


def searchBySubjectAndFilter(request, searchParameters=""):

	# TODO: DO NOT USE AND REMOVE USAGE OF 'features-all-type' FROM HTML.

	searchParametersSplit = searchParameters.split("/")
	subject = searchParametersSplit[0]

	if request.method == "POST" and request.POST["generalQuery"]:
		return redirect("tutoring:searchBySubjectAndFilter", searchParameters=request.POST["generalQuery"])

	try:
		filters = eval(searchParameters.split("/")[1].replace("true", "True").replace("false", "False"))
	except IndexError:
		filters = {'features-inPersonLessons': True, 'features-onlineLessons': True, 'features-pro': True, 'priceFrom': 0, 'priceTo': 100, 'scoreFrom': 0, 'scoreTo': 5000}

	inPersonLessons = filters['features-inPersonLessons'] if 'features-inPersonLessons' in filters else True
	onlineLessons = filters['features-onlineLessons'] if 'features-onlineLessons' in filters else True
	pro = filters['features-pro'] if 'features-pro' in filters else True
	priceFrom = filters['priceFrom'] if 'priceFrom' in filters else 0
	priceTo = filters['priceTo'] if 'priceTo' in filters else 100
	scoreFrom = filters['scoreFrom'] if 'scoreFrom' in filters else 0
	scoreTo = filters['scoreTo'] if 'scoreTo' in filters else 2000

	featuresTicked = [filters[key] for key in filters if 'features' in key]

	if all(x == featuresTicked[0] for x in featuresTicked):
		# If all items in featuresTicked is True OR all items in featuresTicked is False then then show all results.
		tutorList = TutorProfile.objects.filter(subjects__icontains=subject, chargeRate__gte=priceFrom, chargeRate__lte=priceTo).select_related('user').prefetch_related('tutorLessons', 'features')
	else:
		# If only some is ticked, then need to filter results for the ticked criteria.
		tutorList = TutorProfile.objects.filter(subjects__icontains=subject, chargeRate__gte=priceFrom, chargeRate__lte=priceTo).select_related('user').prefetch_related('tutorLessons', 'features')
		requiredFilters = [key.split("-")[1] for key in filters if 'features' in key and filters[key]]
		tutorList = tutorList.filter(features__code__in=requiredFilters)

	tutorList = [item for item in tutorList if scoreFrom <= sum([i.points for i in item.tutorLessons.all()]) <= scoreTo]

	if len(tutorList) == 0:
		messages.error(
			request,
			"Sorry, we couldn't find you a tutor for your search. Try entering something broad."
		)

	# TODO: using defaultFeatureValues check/tick the checkbox in the html page.
	defaultFeatureValues = {"features-inPersonLessons": inPersonLessons, "features-onlineLessons": onlineLessons, "features-pro": pro}

	# If nothing from Features filter is ticked, then show all results.
	# If at least one is ticket, then filter result by the ticked criteria.
	# If all ticked, then filter results by all the ticked criteria.

	tutorFeatureGroupComponent = ComponentGroup.objects.get(code='TUTOR_FEATURE')

	context = {
		"generalQuery": subject,
		"tutorList": tutorList,
		"defaultPriceValues": {"priceFrom": priceFrom, "priceTo": priceTo},
		"defaultScoreValues": {"scoreFrom": scoreFrom, "scoreTo": scoreTo},
		"defaultFeatureValues": defaultFeatureValues,
		"tutorFeatureGroupComponent": tutorFeatureGroupComponent,
	}
	return render(request, 'tutoring/mainpage.html', context)


def getTutorProfileForMainPage(profile):
	ratingValue = tutorOperations.getTutorsAverageRating(profile)
	data = {
		"pk": profile.pk,
		"profilePicture": {
			"url": profile.profilePicture.url if profile.profilePicture else None
		},
		"getTutoringUrl": profile.getTutoringUrl(),
		"user": {
			"first_name": profile.user.first_name,
			"last_name": profile.user.last_name
		},
		"summary": profile.summary,
		"averageRating": {
			"value": ratingValue,
			"stars": generalOperations.convertRatingToStars(ratingValue)
		},
	}
	return data


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