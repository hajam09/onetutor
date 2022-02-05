from django.urls import path
from jira2 import views

app_name = "jira2"

urlpatterns = [
	# path('', views.mainPage, name='main-page'),
	# path('sprint-board/', views.sprintBoard, name='sprintBoard'),
	# path('back-log/', views.backLog, name='backLog'),
	path('ticket/<slug:internalKey>/', views.ticketPage, name='ticket-page'),
	path('projects/', views.projects, name='sprint-boards'),
	path('project/<slug:url>/', views.project, name='project-page'),
]