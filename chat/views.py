from django.shortcuts import render, redirect

def chatpage(request):
	context = {

	}
	return render(request, "chat/chatpage.html", context)
