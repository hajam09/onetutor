from django.shortcuts import render
from accounts.models import TutorProfile

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
		return render(request, "tutoring/mainpage.html",context)

	return render(request, "tutoring/mainpage.html",{})