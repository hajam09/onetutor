from django.urls import path
from django.urls import include
from accounts import views

app_name = "accounts"

urlpatterns = [
	path('login/', views.login, name='login'),
	path('register/', views.register, name='register'),
	path('logout/', views.logout, name='logout'),
	path('profile/select/', views.selectProfile, name='select-profile'),
	path('profile/student/create', views.createStudentProfile, name='create-student-profile'),
	path('profile/tutor/create', views.createTutorProfile, name='create-tutor-profile'),
	path('activate/<uidb64>/<token>', views.activateAccount, name='activate'),
	path('passwordRequest/', views.passwordRequest, name='password-request'),
	path('passwordChange/<uidb64>/<token>', views.passwordChange, name='password-change'),
	path('rules/<slug:ruleType>/', views.rules, name='rules'),
	path('requestDeleteCode/', views.requestDeleteCode, name='requestDeleteCode'),
	path('requestCopyOfData/', views.requestCopyOfData, name='requestCopyOfData'),
	path('user-settings/', views.userSettings, name='user-settings'),
]

# footer links
urlpatterns += [
	path('getInTouch/', views.getInTouch, name='getInTouch'),
]