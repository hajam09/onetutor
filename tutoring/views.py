import json
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
from onetutor.operations.seedDataOperations import runSeedDataInstaller
from tutoring.models import ComponentGroup
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview


def mainpage(request):
	# runSeedDataInstaller()

	subject = request.GET.get('subject')
	sortBy = request.GET.get('sortBy')
	tutorFeature = request.GET.get('tutorFeature', [])
	qualification = request.GET.get('qualification', [])
	myEducationLevel = request.GET.get('myEducationLevel', [])
	rating = int(request.GET.get('rating', -1))
	minimumRate = round(float(request.GET.get('minimumRate', 0.0)), 2)
	maximumRate = round(float(request.GET.get('maximumRate', 9999999999.99)), 2)
	minimumScore = round(float(request.GET.get('minimumScore', 0.0)), 2)
	maximumScore = round(float(request.GET.get('maximumScore', 0.0)), 2)

	if tutorFeature:
		tutorFeature = tutorFeature.split(',')

	if qualification:
		qualification = qualification.split(',')

	if myEducationLevel:
		myEducationLevel = myEducationLevel.split(',')

	context = {
		'subject': subject,
		'showResult': False,
	}

	if subject is not None:
		componentGroupKeys = ['TUTOR_FEATURE', 'EDUCATION_LEVEL', 'QUALIFICATION', 'RATING_FILTER']
		requiredComponentGroup = ComponentGroup.objects.filter(code__in=componentGroupKeys).prefetch_related("components")
		tutorFeatureComponent = [
			{'code': j.code, 'internalKey': j.internalKey, 'checked': j.code in tutorFeature}
			for j in next(i for i in requiredComponentGroup if i.code == componentGroupKeys[0]).components.all()
		]

		myEducationLevelComponent = [
			{'code': j.code, 'internalKey': j.internalKey, 'checked': j.code in myEducationLevel}
			for j in next(i for i in requiredComponentGroup if i.code == componentGroupKeys[1]).components.all()
		]

		qualificationComponent = [
			{'code': j.code, 'internalKey': j.internalKey, 'checked': j.code in qualification}
			for j in next(i for i in requiredComponentGroup if i.code == componentGroupKeys[2]).components.all()
		]

		ratingFilterComponent = [
			{'code': j.reference, 'internalKey': j.internalKey, 'checked': int(j.reference) == rating}
			for j in next(i for i in requiredComponentGroup if i.code == componentGroupKeys[3]).components.all()
		]
		subject = subject.split()

		if "and" in subject:
			requiredOperator = operator.and_
			subject = list(filter("and".__ne__, subject))
		else:
			requiredOperator = operator.or_

		query = reduce(requiredOperator, (Q(subjects__icontains=s) for s in subject))
		tutorList = TutorProfile.objects.filter(query, chargeRate__gte=minimumRate, chargeRate__lte=maximumRate)\
			.select_related('user').prefetch_related('tutorLessons', 'user__tutorReviews', 'features', 'teachingLevels')

		if tutorFeature:
			tutorList = tutorList.filter(features__code__in=tutorFeature)
		if rating > -1 and any(int(i['code']) == rating for i in ratingFilterComponent):
			tutorListTemp = set([t.id for t in tutorList if tutorOperations.getTutorsAverageRating(t) >= rating])
			tutorList = tutorList.filter(id__in=tutorListTemp)
		if myEducationLevel:
			tutorList = tutorList.filter(teachingLevels__code__in=myEducationLevel)

		if sortBy == 'sortPriceLH':
			tutorList = tutorList.order_by('chargeRate')
		elif sortBy == 'sortPriceHL':
			tutorList = tutorList.order_by('-chargeRate')
		# elif sortBy == 'sortScoreLH':
		# 	tutorList = tutorList.order_by('score')
		# elif sortBy == 'SortScoreHL':
		# 	tutorList = tutorList.order_by('-score')

		if not tutorList.exists():
			messages.error(
				request,
				"Sorry, we couldn't find you a tutor for your search. Try entering something broad."
			)

		tutorList = tutorList.distinct()
		page = request.GET.get('page', 1)
		paginator = Paginator(tutorList, 15)

		try:
			tutorList = paginator.page(page)
		except PageNotAnInteger:
			tutorList = paginator.page(1)
		except EmptyPage:
			tutorList = paginator.page(paginator.num_pages)

		context['tutorList'] = tutorList
		context['showResult'] = True
		context['tutorFeatureComponent'] = tutorFeatureComponent
		context['myEducationLevelComponent'] = myEducationLevelComponent
		context['qualificationComponent'] = qualificationComponent
		context['ratingFilterComponent'] = ratingFilterComponent
		context['rate'] = {'minimumRate': minimumRate if minimumRate > 0.0 else None, 'maximumRate': maximumRate if maximumRate < 9999999999.99 else None}
		context['score'] = {'minimumScore': minimumScore if minimumScore > 0.0 else None, 'maximumScore': maximumScore if maximumScore < 0.0 else None}

	return render(request, 'tutoring/mainpage.html', context)


def viewTutorProfile(request, url):

	try:
		tutorProfile = TutorProfile.objects.get(url=url)
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

def viewStudentProfile(request, url):
	print("bb")
	return render(request, "tutoring/studentProfile.html")


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

	questionAnswerCommentJson = [
		{
			'id': i.pk,
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