from django.urls import path

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
    path('cookieConsent/', views.cookieConsent, name='cookieConsent'),
    path('user-settings/', views.userSettings, name='user-settings'),
]

# tutor settings link
# urlpatterns += [
#     path('user-settings/tutor/general', views.tutorGeneralSettings, name='tutor-general-settings'),
#     path('user-settings/tutor/biography', views.tutorBiographySettings, name='tutor-biography-settings'),
#     path('user-settings/tutor/security', views.tutorSecuritySettings, name='tutor-security-settings'),
#     path('user-settings/tutor/notification', views.tutorNotificationSettings, name='tutor-notification-settings'),
#     path('user-settings/tutor/account', views.tutorAccountSettings, name='tutor-account-settings'),
# ]

# student settings link
# urlpatterns += [
#     path('user-settings/student/general', views.studentGeneralSettings, name='student-general-settings'),
#     path('user-settings/tutor/biography', views.studentBiographySettings, name='student-biography-settings'),
#     path('user-settings/student/security', views.studentSecuritySettings, name='student-security-settings'),
#     path('user-settings/student/notification', views.studentNotificationSettings, name='student-notification-settings'),
#     path('user-settings/student/account', views.studentAccountSettings, name='student-account-settings'),
# ]

# footer links
urlpatterns += [
    path('getInTouch/', views.getInTouch, name='getInTouch'),
    path('ourFeatures/', views.ourFeatures, name='ourFeatures'),
]
