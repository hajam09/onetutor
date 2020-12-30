from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Ticket

def mainpage(request):
	if request.method == "POST" and "create_ticket" in request.POST:
		project = request.POST['project']
		issuetype = request.POST['issuetype']
		reporter = request.POST['reporter']
		assignee = request.POST['assignee']
		summary = request.POST['summary']
		description = request.POST['description']
		points = request.POST['points']

		try:
			url = "OneTutor-" + str(Ticket.objects.last().pk)
		except Exception as e:
			url = "OneTutor-0"

		Ticket.objects.create(
			url=url,
			project=project,
			issue_type=issuetype,
			reporter=User.objects.get(pk=reporter),
			assignee=User.objects.get(pk=assignee),
			summary=summary,
			description=description,
			points=points
		)

	context = {
		"tickets": Ticket.objects.all(),
		"superusers": User.objects.filter(is_superuser=True)
	}
	return render(request,"jira/mainpage.html", context)