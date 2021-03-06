from django.urls import path
from django.urls import include
from accounts import views

app_name = "accounts"

urlpatterns = [
	path('login/', views.login, name='login'),
	path('register/', views.register, name='register'),
	path('logout/', views.logout, name='logout'),
	path('profile/select/', views.selectprofile, name='selectprofile'),
	path('profile/student/create', views.create_student_profile, name='create_student_profile'),
	path('profile/tutor/create', views.create_tutor_profile, name='create_tutor_profile'),
	path('profile/tutor/', views.tutorprofile, name='tutorprofile'),
	path('profile/tutor/edit', views.tutorprofileedit, name='tutorprofileedit'),
	path('profile/student/', views.studentprofile, name='studentprofile'),
	path('profile/student/edit', views.studentprofileedit, name='studentprofileedit'),
	path('activate/<uidb64>/<token>', views.activateaccount, name='activate'),
	path('password_request/', views.password_request, name='password_request'),
	path('password_change/<uidb64>/<token>', views.password_change, name='password_change'),
	path('rules/<slug:rule_type>/', views.rules, name='rules'),
	path('requestDeleteCode/', views.requestDeleteCode, name='requestDeleteCode'),
	path('user_settings/', views.user_settings, name='user_settings'),
]