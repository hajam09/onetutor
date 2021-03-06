from accounts.models import Countries
from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import Subject
from accounts.models import TutorProfile
from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader
from django.utils import timezone
from forum.models import Category
from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from jira.models import Sprint
from jira.models import Ticket
from jira.models import TicketComment
from jira.models import TicketImage
from tutoring.models import QAComment
from tutoring.models import QuestionAnswer
import datetime
import math
import operator
import os
import psutil

CPU_USAGE = [0,0,0,0,0,0,0,0,0,0]
RAM_USAGE = [0,0,0,0,0,0,0,0,0,0]

@login_required
def index(request, template="index"):
	metric(request)
	return render(request, "dashboard/"+template+".html")

@login_required
def pages(request):
	# All resource paths end in .html.
	# Pick out the html file name from the url. And load that template.
	try:
		load_template = "dashboard/"+request.path.split('/')[-1]
		html_template = loader.get_template( load_template )
		return HttpResponse(html_template.render({}, request))
		
	except template.TemplateDoesNotExist:

		html_template = loader.get_template( 'dashboard/page-404.html' )
		return HttpResponse(html_template.render({}, request))

	except:
	
		html_template = loader.get_template( 'dashboard/page-500.html' )
		return HttpResponse(html_template.render({}, request))

def metric(request):
	x = jira_task_information()
	# print(x)
	return

def get_all_logged_in_users():
	"""
		this may be not the best solution yet.
	"""
	active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
	user_id_list = []
	for session in active_sessions:
		data = session.get_decoded()
		user_id_list.append(data.get('_auth_user_id', None))

	## request.online_now.count

	return User.objects.filter(id__in=user_id_list).exclude(is_superuser=True)

def get_all_inactive_users():
	"""
		filter for all users last login date.
		check if the last login date exceeds 30 days.
		returns all users that have last_login >= 31 days.
	"""
	thirty_days_ago = datetime.datetime.now().date() - datetime.timedelta(30)
	users = User.objects.filter(Q(last_login__lte=thirty_days_ago))
	return users

def get_all_users_logged_in_today():
	return User.objects.filter(last_login__startswith=timezone.now().date()).exclude(is_superuser=True)

def get_database_size():
	"""
		need to ensure that the file size is received in linux OS
	"""
	file_size =  os.stat(os.getcwd()+"\\db.sqlite3").st_size
	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
		if abs(file_size) < 1024.0:
			return "%3.1f%s%s" % (file_size, unit, 'B')
		file_size /= 1024.0
	return "%.1f%s%s" % (file_size, 'Yi', 'B')

def get_number_of_tutors_and_students():
	all_users = User.objects.all()
	tutors = TutorProfile.objects.all()
	students = StudentProfile.objects.all()
	return [all_users, tutors, students]

def get_account_domains():
	all_users = User.objects.all().exclude(is_superuser=True)
	domains = {}
	for users in all_users:
		try:
			domain_email = users.email.split("@")[1].split(".")[0]
			if domain_email not in domains:
				domains[domain_email] = 1
			else:
				domains[domain_email] += 1
			print(domain_email)
		except:
			pass
	return dict(sorted(domains.items(), key=operator.itemgetter(1),reverse=True))

def get_instance_count_for_each_model():
	instance_count = {
		"countries": Countries.objects.count(),
		"social_connection": SocialConnection.objects.count(),
		"subjects":  Subject.objects.count(),
		"categories": Category.objects.count(),
		"forum_comments": ForumComment.objects.count(),
		"communities": Community.objects.count(),
		"forums": Forum.objects.count(),
		"qa_comments": QAComment.objects.count(),
		"question_answer": QuestionAnswer.objects.count()
	}
	return instance_count

def get_gpu_ram_usage():
	"""
		create two lists to store percentages of each usage.
		store 10 values for each usage.
	"""
	CPU_USAGE.append(psutil.cpu_percent())
	RAM_USAGE.append(psutil.virtual_memory().percent)
	return CPU_USAGE[-10:], RAM_USAGE[-10:]

def get_user_growth_by_month():
	"""
		this may be not the best approach for this problem.
		there is an alternative way which is to group date_joined by month/year
		users_by_month = User.objects.all().extra({'created': "date(date_joined)"}).values('created').annotate(created_count=Count('id')).order_by('-created')
		return last 12 month data.
		data : [[1,10], [2,8], [3,4], [4,13], [5,17], [6,9]]
		ticks: [[1,'January'], [2,'February'], [3,'March'], [4,'April'], [5,'May'], [6,'June']]
	"""
	dates = {}
	for users in User.objects.all().order_by('date_joined'):
		year = str(users.date_joined.year)
		month = "%02d" % (users.date_joined.month,)
		year_month = year+"/"+month
		
		if (year_month not in dates):
			dates[year_month] = 1
		else:
			dates[year_month] += 1

	counter = 1
	data = []
	ticks = []

	for k, v in dates.items():
		data.append([counter, v])
		ticks.append([counter, k])
		counter += 1

	return data[-12:], ticks[-12:]

def jira_task_information():
	"""
		Related data: #of sprints, #of tickets in each issue_type
		#of tickets in each priority, #of tickets by each status.
		#of TicketComment, #of ticketimages and total size of all images.
	"""
	result = {
		"no_of_sprints": Sprint.objects.count(),
		"tickets_in_each_issue_type": list(Ticket.objects.all().values('issue_type').annotate(total=Count('issue_type')).order_by('-total')),
		"tickets_in_each_priority": list(Ticket.objects.all().values('priority').annotate(total=Count('priority')).order_by('-total')),
		"tickets_in_each_status": list(Ticket.objects.all().values('status').annotate(total=Count('status')).order_by('-total')),
		"ticket_image_file_size": convert_file_unit(sum([x.image.size for x in TicketImage.objects.all()])),
		"ticket_comments": 'get by each week and sum'
	}
	return result

def convert_file_unit(size_bytes):
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return "%s %s" % (s, size_name[i])