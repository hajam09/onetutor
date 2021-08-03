from django.urls import path, include
from tutoring import views

app_name = "tutoring"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('tutorprofile/<slug:tutorProfileKey>/', views.viewtutorprofile, name='view-tutor-profile'),
	path('studentprofile/<int:studentId>/', views.viewstudentprofile, name='viewstudentprofile'),
	path('post_question_for_tutor/', views.post_question_for_tutor, name='post_question_for_tutor'),
	path('subject_tag/<slug:tag_name>/', views.subject_tag, name='subject_tag'),
	path('tutor_questions/', views.tutor_questions, name='tutor_questions'),
	path('question_answer_thread/<int:question_id>/', views.question_answer_thread, name='question_answer_thread'),
	path('question_answer/like/', views.like_comment, name='like_comment'),
	path('question_answer/dislike/', views.dislike_comment, name='dislike_comment'),
]