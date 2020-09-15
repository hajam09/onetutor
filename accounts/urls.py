from django.urls import path, include
from accounts import views
app_name = "accounts"
urlpatterns = [
	path('login/', views.login, name='login'),
	path('register/', views.register, name='register'),
	path('logout/', views.logout, name='logout'),
	path('profile/', views.profile, name='profile'),
	path('tutor/profile/', views.tutorprofile, name='tutorprofile'),
	path('tutor/profile/edit', views.tutorprofileedit, name='tutorprofileedit'),
	path('student/profile/', views.studentprofile, name='studentprofile'),
	path('student/profile/edit', views.studentprofileedit, name='studentprofileedit'),
	path('createprofile/', views.createprofile, name='createprofile'),
	path('activate/<uidb64>/<token>', views.activateaccount, name='activate'),
	path('password_request/', views.password_request, name='password_request'),
	path('password_change/<uidb64>/<token>', views.password_change, name='password_change'),
]