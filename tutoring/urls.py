from django.urls import path, include
from tutoring import views

app_name = "tutoring"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('tutorprofile/<slug:tutorProfileKey>/', views.viewTutorProfile, name='view-tutor-profile'),
	path('studentprofile/<int:studentId>/', views.viewstudentprofile, name='viewstudentprofile'),
	path('subject_tag/<slug:tag_name>/', views.subject_tag, name='subject_tag'),
	path('tutors-questions/', views.tutorsQuestions, name='tutors-questions'),
	path('question-answer-thread/<int:questionId>/', views.questionAnswerThread, name='question-answer-thread'),
]