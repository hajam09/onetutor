from django.urls import path
from jira import views

app_name = "jira"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('sprintboard/<slug:sprint_url>/', views.sprintboard, name='sprintboard'),
	path('backlog/', views.backlogView, name='backlog'),
	path('ticket/<slug:ticket_url>/', views.ticketPageView, name='ticketpage'),
	path('ticket/<slug:ticketUrl>/edit', views.editTicketView, name='edit-ticket-view'),
]