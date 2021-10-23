import datetime
import json
import os
from http import HTTPStatus

from deprecated import deprecated
from django.conf import settings
from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from jira.enumerations import IssueType
from jira.enumerations import Priority
from jira.enumerations import Project
from jira.enumerations import Status
from .models import Sprint, Ticket, TicketComment, TicketImage


# ONLY SUPER USER IS ALLOWED!

def mainpage(request):
	today = datetime.date.today()

	try:
		active_sprint = Sprint.objects.get(startDate__lte=today, endDate__gte=today)
	except Sprint.DoesNotExist:
		active_sprint = None

	if active_sprint is not None:
		return redirect('jira:sprintboard', sprint_url=active_sprint.url)
	return redirect('jira:backlog')


def sprintboard(request, sprint_url):

	try:
		active_sprint = Sprint.objects.get(url=sprint_url)
	except Sprint.DoesNotExist:
		# redirect to sprint does not exists page
		pass

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "update_ticket_status":
			moved_ticket_url, new_status = request.GET.get('moved_ticket_url', None), request.GET.get('new_status',
																									  None)

			ticket = Ticket.objects.get(url=moved_ticket_url)
			ticket.status = new_status
			ticket.save()

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		if functionality == "update_ticket_attributes_from_modal":
			new_summary = request.GET.get('new_summary', None)
			new_description = request.GET.get('new_description', None)
			new_column = request.GET.get('new_column', None)
			ticket_id = request.GET.get('ticket_code', None)
			new_priority = request.GET.get('new_priority', None)
			new_issue_type = request.GET.get('new_issue_type', None)

			Ticket.objects.filter(id=ticket_id).update(
				summary=new_summary,
				description=new_description,
				status=new_column,
				priority=new_priority,
				issueType=new_issue_type
			)
			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	sprint_tickets = Ticket.objects.filter(sprint=active_sprint)
	context = {
		"active_sprint": active_sprint,
		"todo_tickets": [i for i in sprint_tickets if i.status == "Open"],
		"prog_tickets": [i for i in sprint_tickets if i.status == "Progress"],
		"done_tickets": [i for i in sprint_tickets if i.status == "Done"],
		"canc_tickets": [i for i in sprint_tickets if i.status == "Cancelled"],
	}
	return render(request, "jira/sprintboard.html", context)


def backlog(request):

	today = datetime.date.today()

	try:
		active_sprint = Sprint.objects.get(startDate__lte=today, endDate__gte=today)
	except Sprint.DoesNotExist:
		active_sprint = None

	if request.method == "POST" and "start_sprint" in request.POST:
		startsprint()
		return redirect('jira:backlog')

	if request.method == "POST" and "create_ticket" in request.POST:
		project = request.POST['project']
		issuetype = request.POST['issuetype']
		priority = request.POST['priority']
		reporter = request.POST['reporter']
		assignee = request.POST['assignee']
		summary = request.POST['summary']
		description = request.POST['description']
		points = request.POST['points']

		if "Jira" in project:
			prefix = "Jira-"
		elif "Dashboard" in project:
			prefix = "Dashboard-"
		else:
			prefix = "OneTutor-"

		try:
			url = prefix + str(Ticket.objects.last().pk)
		except Exception as e:
			url = prefix + "0"

		Ticket.objects.create(
			url=url,
			project=project,
			issueType=issuetype,
			reporter=User.objects.get(pk=reporter),
			assignee=User.objects.get(pk=assignee),
			summary=summary,
			description=description,
			points=points,
			priority=priority
		)
		return redirect('jira:backlog')

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "move_ticket_to_active_sprint":
			moved_ticket_url = request.GET.get('moved_ticket_url', None)

			ticket = Ticket.objects.get(url=moved_ticket_url)
			ticket.status = "Open"
			ticket.sprint = active_sprint
			ticket.save()

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

		elif functionality == "update_ticket_status":
			# moving the ticket from active sprint to backlog
			moved_ticket_url, new_status = request.GET.get('moved_ticket_url', None), request.GET.get('new_status',
																									  None)

			ticket = Ticket.objects.get(url=moved_ticket_url)
			ticket.status = new_status
			ticket.sprint = None
			ticket.save()

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	backlog_tickets = Ticket.objects.filter(status="None")
	context = {
		"bug_tickets": [i for i in backlog_tickets if i.issueType == "Bug"],
		"improvment_tickets": [i for i in backlog_tickets if i.issueType == "Improvement"],
		"story_tickets": [i for i in backlog_tickets if i.issueType == "Story"],
		"task_tickets": [i for i in backlog_tickets if i.issueType == "Task"],
		"test_tickets": [i for i in backlog_tickets if i.issueType == "Test"],
		"epic_tickets": [i for i in backlog_tickets if i.issueType == "Epic"],
		"superusers": User.objects.filter(is_superuser=True),
		"sprint_tickets": Ticket.objects.filter(sprint=active_sprint).exclude(status="None"),
		"active_sprint": active_sprint,
		"project": Project.list(True),
		"issueType": IssueType.list(True),
		"priority": Priority.list(False),
	}
	return render(request, "jira/backlog.html", context)


def ticketPageView(request, ticket_url):

	ticket = Ticket.objects.select_related('reporter', 'assignee', 'sprint').prefetch_related('watchers').get(url=ticket_url)
	ticketComments = TicketComment.objects.filter(ticket=ticket).order_by('-id')

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "watchOrUnwatchIssue":
			if request.user not in ticket.watchers.all():
				ticket.watchers.add(request.user)
				isWatching = True
			else:
				ticket.watchers.remove(request.user)
				isWatching = False

			response = {
				"isWatching": isWatching,
				"newWatchCount": ticket.watchers.count(),
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "createTicketComment":
			comment = request.GET.get('comment', None)
			ticketComment = TicketComment.objects.create(
				ticket=ticket,
				creator=request.user,
				comment=comment,
			)
			response = {
				"statusCode": HTTPStatus.OK,
				"pk": ticketComment.pk,
				"comment": ticketComment.comment,
				"likes": ticketComment.likes.count(),
				"dislikes": ticketComment.dislikes.count(),
			}
			return JsonResponse(response)

		elif functionality == "updateTicketComment":
			commentId = request.GET.get('commentId', None)
			comment = request.GET.get('comment', None)

			thisComment = next((c for c in ticketComments if str(c.id) == commentId), None)
			if thisComment is None:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return JsonResponse(response)

			thisComment.comment = comment
			thisComment.edited = True
			thisComment.save(update_fields=['comment', 'edited'])

			response = {
				"statusCode": HTTPStatus.OK,
				"id": thisComment.id,
				"comment": thisComment.comment,
			}
			return JsonResponse(response)

		elif functionality == "deleteTicketComment":
			commentId = request.GET.get('commentId', None)

			thisComment = next((c for c in ticketComments if str(c.id) == commentId), None)
			if thisComment is None:
				thisComment.delete()

			response = {
				"statusCode": HTTPStatus.OK,
			}
			return JsonResponse(response)

		elif functionality == "likeTicketComment" or functionality == "dislikeTicketComment":
			commentId = request.GET.get('commentId', None)

			thisComment = next((c for c in ticketComments if str(c.id) == commentId), None)
			if thisComment is None:
				response = {
					"statusCode": HTTPStatus.NOT_FOUND,
					"message": "We think this comment has been deleted!"
				}
				return JsonResponse(response)

			if functionality == "likeTicketComment":
				thisComment.like(request)
			else:
				thisComment.dislike(request)

			response = {
				"statusCode": HTTPStatus.OK,
				"likes": thisComment.likes.count(),
				"dislikes": thisComment.dislikes.count(),
			}
			return JsonResponse(response)
		raise Exception("Unknown functionality on ticketpage")

	if request.method == "POST" and "createSubTask" in request.POST:

		project = request.POST['project']
		reporter = request.POST['reporter']
		assignee = request.POST['assignee']

		if "Jira" in project:
			prefix = "Jira-"
		elif "Dashboard" in project:
			prefix = "Dashboard-"
		else:
			prefix = "OneTutor-"

		try:
			url = prefix + str(Ticket.objects.last().pk)
		except Exception as e:
			url = prefix + "0"

		newSubTask = Ticket.objects.create(
			url=url,
			project=project,
			issueType=request.POST['issueType'],
			reporter=User.objects.get(pk=reporter),
			assignee=User.objects.get(pk=assignee),
			summary=request.POST['summary'],
			description=request.POST['description'],
			points=request.POST['points'],
			priority=request.POST['priority']
		)
		ticket.subTask.add(newSubTask)
		return redirect('jira:ticketpage', ticket_url=ticket_url)

	context = {
		"ticket": ticket,
		"ticketImages": ticket.ticketImages.all(),
		"ticketComments": ticketComments,
		"isWatching": True if request.user in ticket.watchers.all() else False,
		"superusers": User.objects.filter(is_superuser=True),
		"subTasks": ticket.subTask.all(),
		"epicLink": Ticket.objects.filter(subTask__in=[ticket]).first(),
		"project": Project.list(True),
		"issueType": IssueType.list(True),
		"priority": Priority.list(True),
	}
	return render(request, "jira/ticketPage.html", context)


def editticket(request, ticket_url):
	ticket = Ticket.objects.get(url=ticket_url)
	ticket_images = TicketImage.objects.filter(ticket=ticket)

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "delete_ticket_image":
			image_object_pk = request.GET.get('image_object_pk', None)
			this_image = TicketImage.objects.get(pk=image_object_pk)

			this_image_location = os.path.join(settings.MEDIA_ROOT, this_image.image.name)
			if os.path.exists(this_image_location):
				os.remove(this_image_location)
				this_image.delete()

			new_ticket_images = TicketImage.objects.filter(ticket=ticket)
			response = {
				"new_ticket_images": serializers.serialize("json", list(new_ticket_images)),
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	if request.method == "POST" and "update_ticket_data" in request.POST:

		assignee = request.POST['assignee']
		description = request.POST['description']
		issuetype = request.POST['issuetype']
		points = request.POST['points']
		priority = request.POST['priority']
		reporter = request.POST['reporter']
		status = request.POST['status']
		summary = request.POST['summary']

		ticket.assignee = User.objects.get(pk=assignee)
		ticket.description = description
		ticket.issueType = issuetype
		ticket.points = points
		ticket.priority = priority
		ticket.reporter = User.objects.get(pk=reporter)
		ticket.status = status
		ticket.summary = summary

		if status != "None":
			if status != "Cancelled" and ticket.sprint is None:
				to_sprint = request.POST['sprint']
				ticket.sprint = Sprint.objects.get(url=to_sprint)
		else:
			# when status is set to none, the ticket is sent to backlog. Set the sprint to none.
			ticket.sprint = None

		ticket.save()

		# creating an instance for each attachement for this ticket
		if "ticket-attachment-files" in request.FILES:
			attachments = request.FILES.getlist('ticket-attachment-files')

			for files in attachments:
				TicketImage.objects.create(
					ticket=ticket,
					image=files
				)

		return redirect('jira:ticketpage', ticket_url=ticket_url)

	context = {
		"ticket": ticket,
		"ticket_images": ticket_images,
		"superusers": User.objects.all(),  # User.objects.filter(is_superuser=True)
		"incomplete_sprints": Sprint.objects.filter(endDate__gte=datetime.date.today()).order_by('startDate'),
		"issueType": IssueType.list(True),
		"priority": Priority.list(False),
		"status": Status.list(True),
	}
	return render(request, "jira/editticket.html", context)


def startsprint():
	today = datetime.date.today()
	try:
		Sprint.objects.get(startDate__lte=today, endDate__gte=today)
	# already a sprint exists as of today. No need to create another.
	except Sprint.DoesNotExist:
		prefix = "sprint-"
		try:
			last_sprint = Sprint.objects.last()
			url = prefix + str(last_sprint.pk)
			Sprint.objects.create(
				url=url,
				startDate=today,
				endDate=today + datetime.timedelta(days=14)
			)
			print(today, today + datetime.timedelta(days=14))
		except Exception as e:
			url = prefix + "0"
			Sprint.objects.create(
				url=url,
				startDate=today,
				endDate=today + datetime.timedelta(days=14)
			)
	return

@deprecated(version='1.2.1', reason="Rather than creating sprint on a recurring task. Let the user create the sprint.")
def createsprint():
	today = datetime.date.today()

	try:
		Sprint.objects.get(startDate__lte=today, endDate_gte=today)
	except Sprint.DoesNotExist:
		prefix = "sprint-"
		try:
			last_sprint = Sprint.objects.last()
			url = prefix + str(last_sprint.pk)
			end_of_last_sprint = last_sprint.end_date
			new_sprint_date = end_of_last_sprint + datetime.timedelta(days=1)
			Sprint.objects.create(
				url=url,
				startDate=new_sprint_date,
				endDate=new_sprint_date+datetime.timedelta(days=14)
			)
			return True
		except Exception as e:
			url = prefix+"0"
		Sprint.objects.create(
			url=url,
			startDate=new_sprint_date,
			endDate=new_sprint_date+datetime.timedelta(days=14)
		)
		return True
	return False