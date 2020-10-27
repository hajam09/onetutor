from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import TutorProfile, Subject
from .models import QuestionAnswer
from django.http import HttpResponse
import json
from django.core import serializers
from datetime import datetime
from deprecated import deprecated

def mainpage(request):
	if request.method == "POST":
		generalQuery = request.POST["generalQuery"]
		location = request.POST["location"]

		tutorList = None
		# user may want to find a particular tutor by name(s).
		if generalQuery and location:
			tutorList = TutorProfile.objects.filter(summary__icontains=generalQuery, location__icontains=location) | \
						TutorProfile.objects.filter(subjects__icontains=generalQuery, location__icontains=location)

		if generalQuery:
			tutorList = TutorProfile.objects.filter(summary__icontains=generalQuery) | \
						TutorProfile.objects.filter(subjects__icontains=generalQuery)

		if location:
			tutorList = TutorProfile.objects.filter(location__icontains=location)

		context = {"tutorList": tutorList}

		if tutorList.count() == 0:
			context["message"] = "Sorry, we couldn't find you a tutor for your search. Try entering something broad."
			context["alert"] = "alert-info" 

		return render(request, "tutoring/mainpage.html", context)

	return render(request, "tutoring/mainpage.html", {})

def viewtutorprofile(request, tutorId):
	try:
		tutorProfile = TutorProfile.objects.get(pk=tutorId)
	except TutorProfile.DoesNotExist:
		return redirect("tutoring:mainpage")
	
	tutorProfile.subjects = tutorProfile.subjects.split(",")
	context = {
		"tutorProfile": tutorProfile,
		"subjects": Subject.objects.all()
	}
	activeQATab = False
	activeQuestion = None

	if request.method == "POST" and "postQuestion" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')
		subjectRelated = request.POST['subject']
		question = request.POST['question']
		QuestionAnswer.objects.create(subject=subjectRelated, question=question, answer="Not answered yet.", questioner=request.user, answerer=tutorProfile.user)
		context["activeQATab"] = True

	if request.method == "POST" and "postAnswer" in request.POST:
		if not request.user.is_authenticated:
			return redirect('accounts:login')
		questionId = request.POST['questionId']
		newAnswer = request.POST['answerText']
		questionAndAnswers = QuestionAnswer.objects.get(pk=questionId)
		questionAndAnswers.answer = newAnswer
		questionAndAnswers.save(update_fields=['answer'])
		context["activeQATab"] = True
		context["activeQuestion"] = questionId

	context["questionAndAnswers"] = QuestionAnswer.objects.filter(answerer=tutorProfile.user).order_by('-id')

	return render(request, "tutoring/tutorprofile.html", context)

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
	this_comment = QuestionAnswer.objects.get(id=int(commentId))
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
		"status_code": 200
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
			"message": "Login to like the question and answer. "
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	commentId = request.GET.get('commentId', None)
	user = User.objects.get(id=int(request.user.pk))
	this_comment = QuestionAnswer.objects.get(id=int(commentId))
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

	date = new_question.date.strftime("%b. %d, %Y,")
	time = datetime.strptime( new_question.date.strftime("%H:%M"), "%H:%M")
	time = time.strftime("%I:%M %p").lower().replace("pm", "p.m.").replace("am", "a.m.")
	date_time = str(date + " " + time)

	response = {
		"status_code": 200,
		"new_question": serializers.serialize("json", [new_question,]),
		"questioner_first_name": new_question.questioner.first_name,
		"questioner_last_name": new_question.questioner.last_name,
		"qa_question": new_question.question,
		"qa_answer": new_question.answer,
		"date_time": date_time,
	}
	return HttpResponse(json.dumps(response), content_type="application/json")