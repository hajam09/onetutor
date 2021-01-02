from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Sprint, Ticket, TicketImage
from django.core import serializers
from http import HTTPStatus
from django.conf import settings
import json, os, datetime
from deprecated import deprecated

def mainpage(request):

	today = datetime.date.today()
	try:
		active_sprint = Sprint.objects.get(start_date__lte=today, end_date__gte=today)
	except Sprint.DoesNotExist:
		active_sprint = None

	if active_sprint != None:
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
			moved_ticket_url, new_status = request.GET.get('moved_ticket_url', None), request.GET.get('new_status', None)

			ticket = Ticket.objects.get(url=moved_ticket_url)
			ticket.status = new_status
			ticket.save()

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")


	context = {
		"active_sprint": active_sprint,
		"todo_tickets": Ticket.objects.filter(status="Open", sprint=active_sprint),
		"prog_tickets": Ticket.objects.filter(status="Progress", sprint=active_sprint),
		"done_tickets": Ticket.objects.filter(status="Done", sprint=active_sprint),
	}
	return render(request,"jira/sprintboard.html", context)

def backlog(request):

	today = datetime.date.today()

	try:
		active_sprint = Sprint.objects.get(start_date__lte=today, end_date__gte=today)
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
		else:
			prefix = "OneTutor-"

		try:
			url = prefix + str(Ticket.objects.last().pk)
		except Exception as e:
			url = prefix+"0"

		Ticket.objects.create(
			url=url,
			project=project,
			issue_type=issuetype,
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
			moved_ticket_url, new_status = request.GET.get('moved_ticket_url', None), request.GET.get('new_status', None)

			ticket = Ticket.objects.get(url=moved_ticket_url)
			ticket.status = new_status
			ticket.sprint = None
			ticket.save()

			response = {
				"status_code": HTTPStatus.OK
			}
			return HttpResponse(json.dumps(response), content_type="application/json")

	context = {
		"bug_tickets": Ticket.objects.filter(status="None", issue_type="Bug"),
		"improvment_tickets": Ticket.objects.filter(status="None", issue_type="Improvement"),
		"story_tickets": Ticket.objects.filter(status="None", issue_type="Story"),
		"task_tickets": Ticket.objects.filter(status="None", issue_type="Task"),
		"test_tickets": Ticket.objects.filter(status="None", issue_type="Test"),
		"epic_tickets": Ticket.objects.filter(status="None", issue_type="Epic"),
		"superusers": User.objects.filter(is_superuser=True),
		"sprint_tickets": Ticket.objects.filter(sprint=active_sprint).exclude(status="None"),
		"active_sprint": active_sprint
	}
	return render(request,"jira/backlog.html", context)

def ticketpage(request, ticket_url):
	ticket = Ticket.objects.get(url=ticket_url)
	ticket_images = TicketImage.objects.filter(ticket=ticket)

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
		"ticket_images": ticket_images,
		"list_of_watchers": list_of_watching_tickets
	}
	return render(request,"jira/ticketpage.html", context)

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

		ticket.assignee=User.objects.get(pk=assignee)
		ticket.description=description
		ticket.issue_type=issuetype
		ticket.points=points
		ticket.priority=priority
		ticket.reporter=User.objects.get(pk=reporter)
		ticket.status=status
		ticket.summary=summary

		ticket.save(update_fields=['assignee', 'description' ,'issue_type' ,'points' ,'priority' ,'reporter' ,'status' ,'summary'])

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
		"superusers": User.objects.all(), #User.objects.filter(is_superuser=True)
	}
	return render(request,"jira/editticket.html", context)

def startsprint():
	today = datetime.date.today()
	try:
		Sprint.objects.get(start_date__lte=today, end_date__gte=today)
		# already a sprint exists as of today. No need to create another.
	except Sprint.DoesNotExist:
		prefix = "sprint-"
		try:
			last_sprint = Sprint.objects.last()
			url = prefix + str(last_sprint.pk)
			Sprint.objects.create(
				url=url,
				start_date=today,
				end_date=today+datetime.timedelta(days=14)
			)
			print(today, today+datetime.timedelta(days=14))
		except Exception as e:
			url = prefix+"0"
			Sprint.objects.create(url=url)
	return

@deprecated(version='1.2.1', reason="Rather than creating sprint on a recurring task. Let the user create the sprint.")
def createsprint():
	today = datetime.date.today()

	try:
		Sprint.objects.get(start_date__lte=today, end_date__gte=today)
	except Sprint.DoesNotExist:
		prefix = "sprint-"
		try:
			last_sprint = Sprint.objects.last()
			url = prefix + str(last_sprint.pk)
			end_of_last_sprint = last_sprint.end_date
			new_sprint_date = end_of_last_sprint + datetime.timedelta(days=1)
			Sprint.objects.create(
				url=url,
				start_date=new_sprint_date,
				end_date=new_sprint_date+datetime.timedelta(days=14)
			)
			return True
		except Exception as e:
			url = prefix+"0"
		Sprint.objects.create(url=url)
		return True
	return False