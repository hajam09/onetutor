from django.urls import path, include
from jira import views

app_name = "jira"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
]