from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
import datetime, os, operator
from django.db.models import Q
from accounts.models import TutorProfile, StudentProfile, Subject, Countries, SocialConnection
from forum.models import Category, Community, Forum, Comment
from tutoring.models import QuestionAnswer, QAComment

@login_required
def index(request, template="index"):
	metric(request)
	return render(request, "dashboard/"+template+".html")

@login_required
def pages(request):
	print("ss")
	context = {}
	# All resource paths end in .html.
	# Pick out the html file name from the url. And load that template.
	try:
		load_template = "dashboard/"+request.path.split('/')[-1]
		html_template = loader.get_template( load_template )
		return HttpResponse(html_template.render(context, request))
		
	except template.TemplateDoesNotExist:

		html_template = loader.get_template( 'dashboard/page-404.html' )
		return HttpResponse(html_template.render(context, request))

	except:
	
		html_template = loader.get_template( 'page-500.html' )
		return HttpResponse(html_template.render(context, request))

def metric(request):
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
		"forum_comments": Comment.objects.count(),
		"communities": Community.objects.count(),
		"forums": Forum.objects.count(),
		"qa_comments": QAComment.objects.count(),
		"question_answer": QuestionAnswer.objects.count()
	}
	return instance_count