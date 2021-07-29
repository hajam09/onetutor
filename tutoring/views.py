import json
from datetime import datetime
from http import HTTPStatus

import pandas
from deprecated import deprecated
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render

from accounts.models import Subject
from accounts.models import TutorProfile
from tutoring.models import QAComment
from tutoring.models import QuestionAnswer
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
				i
				for k in locationList
				for j in generalQueryList
				for i in profiles
				if j.lower() in i.summary.lower() or j.lower() in i.subjects.lower()
				if k.lower() in [i.lower() for i in pandas.json_normalize(i.location, sep='_').to_dict(orient='records')[0].values()]
			]

			context["generalQuery"] = generalQuery
			context["location"] = location
			context["tutorList"] = list(set(tutorList))

		elif generalQuery:

			tutorList = [
				i
				for j in generalQueryList
				for i in profiles
				if j.lower() in i.summary.lower() or j.lower() in i.subjects.lower()
			]

			context["generalQuery"] = generalQuery
			context["tutorList"] = list(set(tutorList))

		elif location:

			tutorList = [
				i
				for i in profiles
				for k in locationList
				if k.lower() in [i.lower() for i in pandas.json_normalize(i.location, sep='_').to_dict(orient='records')[0].values()]
			]

			context["location"] = location
			context["tutorList"] = list(set(tutorList))

		else:
			context["tutorList"] = []

		if len(context["tutorList"]) == 0:
			messages.error(
				request,
				'Sorry, we couldn\'t find you a tutor for your search. Try entering something broad.'
			)

	return render(request, 'tutoring/mainpage.html', context)

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
def tutor_questions(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect("accounts:selectprofile")

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "post_answer":
			question_id, new_answer = request.GET.get('question_id', None), request.GET.get('new_answer', None)

			try:
				this_qa = QuestionAnswer.objects.get(pk=int(question_id))
			except QuestionAnswer.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": 'We think this question has been deleted!'
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_qa.answer = new_answer
			this_qa.save(update_fields=['answer'])
			response = {
				"this_qa": serializers.serialize("json", [this_qa,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		elif functionality == "delete_question":
			question_id = request.GET.get('question_id', None)
			try:
				QuestionAnswer.objects.get(pk=int(question_id)).delete()
				response = {
					"status_code": HTTPStatus.OK
				}
				return HttpResponse(json.dumps(response), content_type="application/json")
			except QuestionAnswer.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			response = {
				"status_code": HTTPStatus.BAD_REQUEST,
				"message": "Bad Request"
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		raise Exception("Unknown functionality tutor_questions")

	context = {
		"questionAndAnswers": QuestionAnswer.objects.filter(answerer=tutorProfile.user).select_related('questioner', 'answerer').prefetch_related('likes', 'dislikes').order_by('-id')
	}
	return render(request, "tutoring/tutor_questions.html", context)

def viewstudentprofile(request, studentId):
	print("bb")
	return render(request, "tutoring/studentprofile.html", {})

def question_answer_thread(request, question_id):
	qa_object = QuestionAnswer.objects.select_related('questioner').get(id=question_id)

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		response_message = {
			"post_comment": "Login to post a comment.",
			"like_comment": "Login to like the comment.",
			"dislike_comment": "Login to dislike the comment.",
			"update_comment": "Login to update the comment.",
		}

		if not request.user.is_authenticated:
			response = {
				"status_code": 401,
				"message": response_message[functionality]
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "post_comment":
			comment = request.GET.get('comment', None)
			new_qa_comment = QAComment.objects.create(
				question_answer = qa_object,
				creator = request.user,
				comment = comment,
			)
			response = {
				"new_qa_comment": serializers.serialize("json", [new_qa_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "like_comment":
			# TODO: Manual test the implementation.
			comment_id = request.GET.get('commentId', None)

			try:
				this_comment = QAComment.objects.get(id=int(comment_id))
			except QAComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": 'We think this comment has been deleted!'
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_comment.increase_qa_comment_likes(request)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "dislike_comment":
			# TODO: Manual test the implementation.
			comment_id = request.GET.get('commentId', None)

			try:
				this_comment = QAComment.objects.get(id=int(comment_id))
			except QAComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": 'We think this comment has been deleted!'
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_comment.increase_qa_comment_dislikes(request)

			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "delete_qa_comment":
			comment_id = request.GET.get('comment_id', None)
			try:
				QAComment.objects.get(pk=int(comment_id)).delete()
				response = {
					"status_code": HTTPStatus.OK
				}
				return HttpResponse(json.dumps(response), content_type="application/json")
			except QAComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			response = {
				"status_code": HTTPStatus.BAD_REQUEST,
				"message": "Bad Request"
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "update_comment":
			comment_id, comment_text = request.GET.get('comment_id', None), request.GET.get('comment_text', None)

			try:
				this_comment = QAComment.objects.get(id=int(comment_id))
			except QAComment.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": 'We think this comment has been deleted!'
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			this_comment.comment = comment_text
			this_comment.edited = True
			this_comment.save(update_fields=['comment', 'edited'])
			response = {
				"this_comment": serializers.serialize("json", [this_comment,]),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		raise Exception("Unknown functionality question_answer_thread")

	context = {
		"qa": qa_object,
		"qa_comments": QAComment.objects.filter(question_answer=qa_object).select_related('creator').prefetch_related('likes', 'dislikes').order_by('-id')
	}
	return render(request, "tutoring/question_answer_thread.html", context)

@deprecated(reason="Implemented in viewtutorprofile views.")
def like_comment(request):
	# TODO: Manual test the implementation. Check if used.
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to like the question and answer. "
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	comment_id = request.GET.get('commentId', None)

	try:
		this_comment = QuestionAnswer.objects.get(id=int(comment_id))
	except QuestionAnswer.DoesNotExist:
		response = {
			"status_code": HTTPStatus.NOT_FOUND,
			"message": 'We think this question has been deleted!'
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if(request.user not in this_comment.likes.all()):
		this_comment.likes.add(request.user)
	else:
		this_comment.likes.remove(request.user)

	if(request.user in this_comment.dislikes.all()):
		this_comment.dislikes.remove(request.user)

	response = {
		"this_comment": serializers.serialize("json", [this_comment,]),
		"status_code": HTTPStatus.OK
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

@deprecated(reason="Implemented in viewtutorprofile views.")
def dislike_comment(request):
	# TODO: Manual test the implementation. Check if used.
	if not request.is_ajax():
		response = {
			"status_code": 403,
			"message": "Bad Request"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if not request.user.is_authenticated:
		response = {
			"status_code": 401,
			"message": "Login to dislike the question and answer. "
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	comment_id = request.GET.get('commentId', None)

	try:
		this_comment = QuestionAnswer.objects.get(id=int(comment_id))
	except QuestionAnswer.DoesNotExist:
		response = {
			"status_code": HTTPStatus.NOT_FOUND,
			"message": 'We think this question has been deleted!'
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	if(request.user not in this_comment.dislikes.all()):
		this_comment.dislikes.add(request.user)
	else:
		this_comment.dislikes.remove(request.user)

	if(request.user in this_comment.likes.all()):
		this_comment.likes.remove(request.user)

	response = {
		"this_comment": serializers.serialize("json", [this_comment,]),
		"status_code": 200
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

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

@deprecated(version='1.2.1', reason="Prevents linebreaksbr tag to be applied to the question and answer textfield.")
def post_question_for_tutor(request):
	if not request.user.is_authenticated:
		response = {
			"status_code": 403,
			"authenticated": False
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	subject = request.GET.get('subject', None)
	question = request.GET.get('question', None)
	tutorId = request.GET.get('tutorId', None)

	tutorProfile = TutorProfile.objects.get(pk=tutorId)

	new_question = QuestionAnswer.objects.create(subject=subject, question=question,
		answer="Not answered yet.", questioner=request.user, answerer=tutorProfile.user)

	response = {
		"status_code": 200,
		"new_question": serializers.serialize("json", [new_question,]),
		"questioner_first_name": new_question.questioner.first_name,
		"questioner_last_name": new_question.questioner.last_name,
		"qa_question": new_question.question,
		"qa_answer": new_question.answer,
		"date_time": vanilla_JS_date_conversion(new_question.date),
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

def vanilla_JS_date_conversion(python_date):
	date = python_date.strftime("%b. %d, %Y,")
	time = datetime.strptime( python_date.strftime("%H:%M"), "%H:%M")
	time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
	date_time = str(date + " " + time)
	return date_time