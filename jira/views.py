import datetime
import json
import os
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.models import User
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
		return redirect('jira:sprintboard', sprintUrl=active_sprint.url)
	return redirect('jira:backlog')


def sprintBoardView(request, sprintUrl):

	try:
		activeSprint = Sprint.objects.get(url=sprintUrl)
	except Sprint.DoesNotExist:
		return redirect('jira:backlog')  # or redirect to 404 page

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)
		ticketUrl = request.GET.get('ticketUrl', None)
		ticket = Ticket.objects.get(url=ticketUrl)

		if functionality == "moveTicketToOpen":
			ticket.status = "Open"

		if functionality == "moveTicketToProgress":
			ticket.status = "Progress"

		if functionality == "moveTicketToDone":
			ticket.status = "Done"

		if functionality == "updateTicketAttributesFromModal":
			ticket.issueType = request.GET.get('newIssueType', None)
			ticket.summary = request.GET.get('newSummary', None)
			ticket.description = request.GET.get('newDescription', None)
			ticket.status = request.GET.get('newStatus', None)
			ticket.priority = request.GET.get('newPriority', None)
			# ticket.points = request.GET.get('newPoint', None)

		ticket.save()

		response = {
			"statusCode": HTTPStatus.OK
		}
		return JsonResponse(response)

	context = {
		"activeSprint": activeSprint,
		"sprintTickets": Ticket.objects.filter(sprint=activeSprint),
	}
	return render(request, "jira/sprintBoard.html", context)


def backlogView(request):

	today = datetime.date.today()

	try:
		activeSprint = Sprint.objects.get(startDate__lte=today, endDate__gte=today)
	except Sprint.DoesNotExist:
		activeSprint = None

	if request.method == "POST" and "startNewSprint" in request.POST:
		activeSprint = startNewSprint()

	if request.method == "POST" and "createNewTicket" in request.POST:
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
		except AttributeError as exception:
			url = prefix + "0"

		Ticket.objects.create(
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

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "moveTicketToActiveSprint":
			movedTicketUrl = request.GET.get('movedTicketUrl', None)

			ticket = Ticket.objects.get(url=movedTicketUrl)
			ticket.status = "Open"
			ticket.sprint = activeSprint
			ticket.save()

			response = {
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

		elif functionality == "moveTicketToBacklog":
			movedTicketUrl = request.GET.get('movedTicketUrl', None)

			ticket = Ticket.objects.get(url=movedTicketUrl)
			ticket.status = "None"
			ticket.sprint = None
			ticket.save()

			response = {
				"statusCode": HTTPStatus.OK
			}
			return JsonResponse(response)

	backlogTickets = Ticket.objects.filter(status=Status.NONE)

	# Think about list comprehension for each line or one for-loop for all.
	tickets = {
		"bugTickets": [i for i in backlogTickets if i.issueType == IssueType.BUG.value],
		"improvementTickets": [i for i in backlogTickets if i.issueType == IssueType.IMPROVEMENT.value],
		"storyTickets": [i for i in backlogTickets if i.issueType == IssueType.STORY.value],
		"taskTickets": [i for i in backlogTickets if i.issueType == IssueType.TASK.value],
		"testTickets": [i for i in backlogTickets if i.issueType == IssueType.TEST.value],
		"epicTickets": [i for i in backlogTickets if i.issueType == IssueType.EPIC.value],
		"sprintTickets": Ticket.objects.filter(sprint=activeSprint).exclude(status=Status.NONE)
	}

	context = {
		"tickets": tickets,
		"superUsers": User.objects.filter(is_superuser=True),
		"activeSprint": activeSprint,
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


def editTicketView(request, ticketUrl):

	ticket = Ticket.objects.select_related('reporter', 'assignee', 'sprint').get(url=ticketUrl)

	if request.is_ajax():
		functionality = request.GET.get('functionality', None)

		if functionality == "deleteTicketImage":
			imagePk = request.GET.get('imagePk', None)
			getImage = TicketImage.objects.get(pk=imagePk)

			imageLocation = os.path.join(settings.MEDIA_ROOT, getImage.image.name)
			if os.path.exists(imageLocation):
				os.remove(imageLocation)
				getImage.delete()

			remainingTicketImages = TicketImage.objects.filter(ticket=ticket)
			response = {
				"statusCode": HTTPStatus.OK,
				"remainingTicketImages": [{"pk": i.pk, "image": "/media/"+str(i.image)} for i in remainingTicketImages],
			}
			return JsonResponse(response)

	if request.method == "POST" and "updateTicket" in request.POST:

		assignee = request.POST['assignee']
		reporter = request.POST['reporter']
		status = request.POST['status']

		ticket.assignee = User.objects.get(pk=assignee)
		ticket.description = request.POST['description']
		ticket.issueType = request.POST['issueType']
		ticket.points = request.POST['points']
		ticket.priority = request.POST['priority']
		ticket.reporter = User.objects.get(pk=reporter)
		ticket.status = status
		ticket.summary = request.POST['summary']

		if status != "None":
			if status != "Cancelled" and ticket.sprint is None:
				toSprint = request.POST['sprint']
				ticket.sprint = Sprint.objects.get(url=toSprint)
		else:
			# when status is set to none, the ticket is sent to backlog. Set the sprint to none.
			ticket.sprint = None

		ticket.save()

		# creating an instance for each attachment for this ticket
		if "ticket-attachment-files" in request.FILES:
			attachments = request.FILES.getlist('ticket-attachment-files')

			for files in attachments:
				TicketImage.objects.create(
					ticket=ticket,
					image=files
				)

		return redirect('jira:ticketpage', ticket_url=ticketUrl)

	context = {
		"ticket": ticket,
		"ticketImages": ticket.ticketImages.all(),
		"superUsers": User.objects.all(),  # User.objects.filter(is_superuser=True)
		"incompleteSprints": Sprint.objects.filter(endDate__gte=datetime.date.today()).order_by('startDate'),
		"issueType": IssueType.list(True),
		"priority": Priority.list(False),
		"status": Status.list(True),
	}
	return render(request, "jira/editTicket.html", context)


def startNewSprint():
	today = datetime.date.today()

	# if the user wants to start a new sprint, then start it but close any open ones.
	Sprint.objects.filter(startDate__lte=today, endDate__gte=today).update(endDate=today)

	prefix = "sprint-"

	try:
		url = prefix + str(Sprint.objects.last().pk)
	except AttributeError as exception:
		url = prefix + "0"
		print(exception)

	newSprint = Sprint.objects.create(
		url=url,
		startDate=today,
		endDate=today + datetime.timedelta(days=14)
	)

	return newSprint
