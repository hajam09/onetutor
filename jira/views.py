from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Ticket
from django.core import serializers
from http import HTTPStatus
import json

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

def ticketpage(request, ticket_url):
	ticket = Ticket.objects.get(url=ticket_url)

	if request.is_ajax():
		list_of_watched_tickets = Ticket.objects.filter(watchers__id=request.user.pk)

		if(ticket not in list_of_watched_tickets):
			request.user.watchers.add(ticket)
		else:
			request.user.watchers.remove(ticket)

		updated_watching_ticket = list(Ticket.objects.filter(watchers__id=request.user.pk).values_list('id', flat=True))
		response = {
			"updated_watching_ticket": updated_watching_ticket,
			"new_watch_count_for_this_ticket": Ticket.objects.get(url=ticket_url).watchers.count(),
			"status_code": HTTPStatus.OK
		}
		return HttpResponse(json.dumps(response), content_type="application/json")

	list_of_watching_tickets = list(Ticket.objects.filter(watchers__id=request.user.pk).values_list('id', flat=True))
	context = {
		"ticket": ticket,
		"list_of_watchers": list_of_watching_tickets
	}
	return render(request,"jira/ticketpage.html", context)