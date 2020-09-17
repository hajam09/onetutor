from django.urls import path, include
from tutoring import views

app_name = "tutoring"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('view/tutorprofile/<int:tutorId>/', views.viewtutorprofile, name='viewtutorprofile'),
	path('view/studentprofile/<int:studentId>/', views.viewstudentprofile, name='viewstudentprofile'),
]