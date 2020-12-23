from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import TutorProfile, Subject
from .models import QuestionAnswer
from django.http import HttpResponse
import json
from django.core import serializers
from datetime import datetime
from deprecated import deprecated
from http import HTTPStatus
from django.contrib.auth.decorators import login_required

def mainpage(request):
	if request.method == "POST":
		generalQuery = request.POST["generalQuery"]
		location = request.POST["location"]
		context = {}

		tutorList = None
		# user may want to find a particular tutor by name(s).
		if generalQuery and location:
			tutorList = TutorProfile.objects.filter(summary__icontains=generalQuery, location__icontains=location) | \
						TutorProfile.objects.filter(subjects__icontains=generalQuery, location__icontains=location)
			context["generalQuery"] = generalQuery
			context["location"] = location

		elif generalQuery:
			tutorList = TutorProfile.objects.filter(summary__icontains=generalQuery) | \
						TutorProfile.objects.filter(subjects__icontains=generalQuery)
			context["generalQuery"] = generalQuery

		elif location:
			tutorList = TutorProfile.objects.filter(location__icontains=location)
			context["location"] = location

		else:
			context["message"] = "Search for a tutor again!"
			context["alert"] = "alert-danger"
			return render(request, "tutoring/mainpage.html", context)

		context["tutorList"] = tutorList

		if tutorList.count() == 0:
			context["message"] = "Sorry, we couldn't find you a tutor for your search. Try entering something broad."
			context["alert"] = "alert-info" 

		return render(request, "tutoring/mainpage.html", context)

	return render(request, "tutoring/mainpage.html", {})

def viewtutorprofile(request, tutor_secondary_key):
	print(tutor_secondary_key)
	try:
		tutorProfile = TutorProfile.objects.get(secondary_key=tutor_secondary_key)
	except TutorProfile.DoesNotExist:
		return redirect("tutoring:mainpage")
	
	tutorProfile.subjects = tutorProfile.subjects.replace(", ", ",").split(",")

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "post_question":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to post a question."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			subject, question = request.GET.get('subject', None), request.GET.get('question', None)
			new_qa = QuestionAnswer.objects.create(
				subject=subject,
				question=question,
				answer="Not answered yet.",
				questioner=request.user,
				answerer=tutorProfile.user
			)
			response = {
				"new_qa": serializers.serialize("json", [new_qa,]),
				"created_date": vanilla_JS_date_conversion(new_qa.date),
				"questioner_first_name": new_qa.questioner.first_name,
				"questioner_last_name": new_qa.questioner.last_name,
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		elif functionality == "post_answer":
			if not request.user.is_authenticated:
				response = {
					"status_code": 401,
					"message": "Login to post an answer."
				}
				return HttpResponse(json.dumps(response), content_type="application/json")

			question_id, new_answer = request.GET.get('question_id', None), request.GET.get('new_answer', None)

			try:
				this_qa = QuestionAnswer.objects.get(pk=int(question_id))
			except QuestionAnswer.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this question has been deleted!"
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

		raise Exception("Unknown functionality viewtutorprofile")

	context = {
		"tutorProfile": tutorProfile,
		"subjects": Subject.objects.all(),
		"questionAndAnswers": QuestionAnswer.objects.filter(answerer=tutorProfile.user).order_by('-id')
	}

	return render(request, "tutoring/tutorprofile.html", context)

@login_required
def tutor_questions(request):
	try:
		tutorProfile = TutorProfile.objects.get(user=request.user.id)
	except TutorProfile.DoesNotExist:
		return redirect("accounts:createprofile")

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "post_answer":
			question_id, new_answer = request.GET.get('question_id', None), request.GET.get('new_answer', None)

			try:
				this_qa = QuestionAnswer.objects.get(pk=int(question_id))
			except QuestionAnswer.DoesNotExist:
				response = {
					"status_code": HTTPStatus.NOT_FOUND,
					"message": "We think this question has been deleted!"
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
		"questionAndAnswers": QuestionAnswer.objects.filter(answerer=tutorProfile.user).order_by('-id')
	}
	return render(request, "tutoring/tutor_questions.html", context)

def viewstudentprofile(request, studentId):
	print("bb")
	return render(request, "tutoring/studentprofile.html", {})

def like_comment(request):
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

	commentId = request.GET.get('commentId', None)
	user = User.objects.get(id=int(request.user.pk))

	try:
		this_comment = QuestionAnswer.objects.get(id=int(commentId))
	except QuestionAnswer.DoesNotExist:
		response = {
			"status_code": HTTPStatus.NOT_FOUND,
			"message": "We think this question has been deleted!"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	list_of_liked = QuestionAnswer.objects.filter(likes__id=user.pk)
	list_of_disliked = QuestionAnswer.objects.filter(dislikes__id=user.pk)

	if(this_comment not in list_of_liked):
		user.likes.add(this_comment)
	else:
		user.likes.remove(this_comment)

	if(this_comment in list_of_disliked):
		user.dislikes.remove(this_comment)

	response = {
		"this_comment": serializers.serialize("json", [this_comment,]),
		"status_code": HTTPStatus.OK
	}
	return HttpResponse(json.dumps(response), content_type="application/json")

def dislike_comment(request):
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

	commentId = request.GET.get('commentId', None)
	user = User.objects.get(id=int(request.user.pk))

	try:
		this_comment = QuestionAnswer.objects.get(id=int(commentId))
	except QuestionAnswer.DoesNotExist:
		response = {
			"status_code": HTTPStatus.NOT_FOUND,
			"message": "We think this question has been deleted!"
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	list_of_liked = QuestionAnswer.objects.filter(likes__id=user.pk)
	list_of_disliked = QuestionAnswer.objects.filter(dislikes__id=user.pk)

	if(this_comment not in list_of_disliked):
		user.dislikes.add(this_comment)
	else:
		user.dislikes.remove(this_comment)
		
	if(this_comment in list_of_liked):
		user.likes.remove(this_comment)

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