from datetime import datetime
from http import HTTPStatus

import pandas
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from accounts.models import Subject
from accounts.models import TutorProfile
from tutoring.models import QuestionAnswer
from tutoring.models import QuestionAnswerComment
from tutoring.models import TutorReview


def mainpage(request):
	context = {}

	if request.method == "POST":

		generalQuery = request.POST["generalQuery"]
		location = request.POST["location"]

		generalQueryList = generalQuery.split()
		locationList = location.split()

		profiles = TutorProfile.objects.all().select_related('user')

		# user may want to find a particular tutor by name(s).
		if generalQuery and location:
			"""
			# Explanation #
			generalQueryList = ['English', 'Maths', 'tutorname', ...]
			locationList = ['GB', 'London', 'Manchester', ...]
			For each TutorProfile, if any items in generalQueryList is found in summary
			or subjects AND any items in locationList is found in location JSON converted
			to flat JSON with keys and values to lowercase, then its the required tutor.
			
			for i in profiles:
				for j in generalQueryList:
					if j.lower() in i.summary.lower() or j.lower() in i.subjects.lower():
						for k in locationList:
							flatLocation = pandas.json_normalize(i.location, sep='_').to_dict(orient='records')[0].values()
							lowerCaseKV = [i.lower() for i in flatLocation]
							if k.lower() in lowerCaseKV:
								tutorList.append(i)
			"""

			tutorList = [
				{
					"pk": i.pk,
					"profilePicture": {
						"url": i.profilePicture.url if i.profilePicture else None
					},
					"getTutoringUrl": i.getTutoringUrl(),
					"user": {
						"first_name": i.user.first_name,
						"last_name": i.user.last_name
					},
					"summary": i.summary,
					"averageRating": ratingToStars(i),
				}
				for k in locationList
				for j in generalQueryList
				for i in profiles
				if j.lower() in i.summary.lower() or j.lower() in i.subjects.lower()
				if k.lower() in [i.lower() for i in pandas.json_normalize(i.location, sep='_').to_dict(orient='records')[0].values()]
			]

			context["generalQuery"] = generalQuery
			context["location"] = location
			context["tutorList"] = list(tutorList)

		elif generalQuery:

			tutorList = [
				{
					"pk": i.pk,
					"profilePicture": {
						"url": i.profilePicture.url if i.profilePicture else None
					},
					"getTutoringUrl": i.getTutoringUrl(),
					"user": {
						"first_name": i.user.first_name,
						"last_name": i.user.last_name
					},
					"summary": i.summary,
					"averageRating": ratingToStars(i),
				}
				for j in generalQueryList
				for i in profiles
				if j.lower() in i.summary.lower() or j.lower() in i.subjects.lower()
			]

			context["generalQuery"] = generalQuery
			context["tutorList"] = list(tutorList)

		elif location:

			tutorList = [
				{
					"pk": i.pk,
					"profilePicture": {
						"url": i.profilePicture.url if i.profilePicture else None
					},
					"getTutoringUrl": i.getTutoringUrl(),
					"user": {
						"first_name": i.user.first_name,
						"last_name": i.user.last_name
					},
					"summary": i.summary,
					"averageRating": ratingToStars(i),
				}
				for i in profiles
				for k in locationList
				if k.lower() in [i.lower() for i in pandas.json_normalize(i.location, sep='_').to_dict(orient='records')[0].values()]
			]

			context["location"] = location
			context["tutorList"] = list(tutorList)

		else:
			context["tutorList"] = []

		if len(context["tutorList"]) == 0:
			messages.error(
				request,
				'Sorry, we couldn\'t find you a tutor for your search. Try entering something broad.'
			)

	return render(request, 'tutoring/mainpage.html', context)


def ratingToStars(tutor):
	# TODO: Need to optimise the tutor reviews rating points. Would be very slow for large number of tutor profiles.
	tutorReviewsObjects = tutor.user.tutorReviews
	outOfPoints = tutorReviewsObjects.count() * 5
	sumOfRating = sum(list(tutorReviewsObjects.values_list('rating', flat=True)))

	try:
		numberOfStars = sumOfRating * 5 / outOfPoints
		nearest05 = round(numberOfStars * 2) / 2
	except ZeroDivisionError:
		return ""

	starsAsString = "".join(['<i class="fas fa-star"></i>' for _ in range(int(nearest05))])

	if ".5" in str(nearest05):
		starsAsString += '<i class="fas fa-star-half"></i>'

	return starsAsString


def viewtutorprofile(request, tutorProfileKey):

	try:
		tutorProfile = TutorProfile.objects.get(secondary_key=tutorProfileKey)
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
				'createdDate': vanilla_JS_date_conversion(questionAnswer.date),
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
				'createdDate': vanilla_JS_date_conversion(tutorReview.date),
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

		raise Exception("Unknown functionality viewtutorprofile")

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
		return redirect("accounts:selectprofile")

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
				'date': vanilla_JS_date_conversion(questionAnswerComment.date),
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


def subject_tag(request, tag_name):
	tutor_list = TutorProfile.objects.filter(subjects__icontains=tag_name)

	list_of_subjects = []

	for tutors in tutor_list:
		list_subject = tutors.subjects.replace(", ", ",").split(",")
		unique_subjects = [subject for subject in list_subject if subject not in list_of_subjects]
		list_of_subjects.extend(unique_subjects)

	context = {
		"tutor_list": tutor_list,
		"list_of_subjects": list_of_subjects
	}
	return render(request, "tutoring/resultbysubjects.html", context)

def vanilla_JS_date_conversion(python_date):
	date = python_date.strftime("%b. %d, %Y,")
	time = datetime.strptime( python_date.strftime("%H:%M"), "%H:%M")
	time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
	date_time = str(date + " " + time)
	return date_time