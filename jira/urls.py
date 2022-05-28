from django.urls import path

from jira import views
from jira.api import TicketObjectDetailsApiEventVersion1Component

app_name = "jira"

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('sprintboard/<slug:sprintUrl>/', views.sprintBoardView, name='sprintboard'),
    path('backlog/', views.backlogView, name='backlog'),
    path('ticket/<slug:ticket_url>/', views.ticketPageView, name='ticketpage'),
    path('ticket/<slug:ticketUrl>/edit', views.editTicketView, name='edit-ticket-view'),
]

# api
urlpatterns += [
    path(
        'api/v1/ticketObjectDetailsApiEventVersion1Component',
        TicketObjectDetailsApiEventVersion1Component.as_view(),
        name='ticketObjectDetailsApiEventVersion1Component'
    ),
]
