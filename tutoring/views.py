from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from accounts.models import TutorProfile
from .models import QuestionAnswer

def mainpage(request):
	if request.method == "POST":
		generalQuery = request.POST["generalQuery"]
		location = request.POST["location"]

		tutorList = None
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
		print(context)
		return render(request, "tutoring/mainpage.html", context)

	return render(request, "tutoring/mainpage.html", {})

def viewtutorprofile(request, tutorId):
	try:
		tutorProfile = TutorProfile.objects.get(pk=tutorId)
	except TutorProfile.DoesNotExist:
		return redirect("tutoring:mainpage")
	
	tutorProfile.subjects = tutorProfile.subjects.split(",")

	if request.method == "POST" and "postQuestion" in request.POST and request.user.is_authenticated:
		subjectRelated = request.POST['subject-related']
		question = request.POST['question']
		QuestionAnswer.objects.create(subject=subjectRelated, question=question, questioner=request.user, answerer=tutorProfile.user)

	questionAndAnswers = QuestionAnswer.objects.filter(answerer=tutorProfile.user)
	for i in questionAndAnswers:
		i.subject = i.subject.split(",")

	return render(request, "tutoring/tutorprofile.html", {"tutorProfile": tutorProfile, "questionAndAnswers": questionAndAnswers})

def viewstudentprofile(request, studentId):
	print("bb")
	return render(request, "tutoring/studentprofile.html", {})