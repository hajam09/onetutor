from django.urls import path, include
from jira import views

app_name = "jira"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('ticket/<slug:ticket_url>/', views.ticketpage, name='ticketpage'),
	path('ticket/<slug:ticket_url>/edit', views.editticket, name='editticket'),
]