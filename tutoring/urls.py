from django.urls import path, include
from tutoring import views

app_name = "tutoring"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('view/tutorprofile/<slug:tutor_secondary_key>/', views.viewtutorprofile, name='viewtutorprofile'),
	path('view/studentprofile/<int:studentId>/', views.viewstudentprofile, name='viewstudentprofile'),
	path('like_comment/', views.like_comment, name='like_comment'),
	path('dislike_comment/', views.dislike_comment, name='dislike_comment'),
	path('post_question_for_tutor/', views.post_question_for_tutor, name='post_question_for_tutor'),
	path('subject_tag/<slug:tag_name>/', views.subject_tag, name='subject_tag')
]