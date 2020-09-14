from django.shortcuts import render

def mainpage(request):
	if request.method == "POST":
		search = request.POST["search"]
		location = request.POST["location"]

	return render(request, "tutoring/mainpage.html",{})