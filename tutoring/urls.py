from django.conf.urls import url
from django.urls import path

from tutoring import views

app_name = "tutoring"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	url(r'^tutors/(?P<searchParameters>.*)/$', views.searchBySubjectAndFilter, name='searchBySubjectAndFilter'),
	path('tutorprofile/<slug:url>/', views.viewTutorProfile, name='view-tutor-profile'),
	path('studentprofile/<int:studentId>/', views.viewstudentprofile, name='viewstudentprofile'),
	path('tutors-questions/', views.tutorsQuestions, name='tutors-questions'),
	path('question-answer-thread/<int:questionId>/', views.questionAnswerThread, name='question-answer-thread'),
]