from django.urls import path

from accounts import views
from accounts.api import CookieConsentApiEventVersion1Component
from accounts.api import RequestDeleteCodeApiEventVersion1Component

app_name = 'accounts'

urlpatterns = [
    path('login/', views.loginView, name='login-view'),
    path('logout/', views.logoutView, name='logout-view'),
    path('register/', views.registrationView, name='register-view'),
    path('activate-account/<base64>/<token>/', views.activateAccountView, name='activate-account-view'),
    path('password-reset-request/', views.passwordResetRequestView, name='password-reset-request-view'),
    path('password-reset-confirm/<base64>/<token>', views.passwordResetConfirmView, name='password-reset-confirm-view'),

    path("create-profile/", views.CreateProfileViewApi.as_view(), name="create-profile"),
    path("settings/", views.SettingsView.as_view(), name="settings-view"),

    path("rules/<slug:ruleType>/", views.rules, name="rules"),
    path("requestDeleteCode/", views.requestDeleteCode, name="requestDeleteCode"),
    path("requestCopyOfData/", views.requestCopyOfData, name="requestCopyOfData"),
    path("cookieConsent/", views.cookieConsent, name="cookieConsent"),
]

# general profile link
urlpatterns += [
    # path('user-settings/<slug:profile>/general', views.profileGeneralSettings, name='profile-general-settings'),
    # path('user-settings/<slug:profile>/security', views.profileSecuritySettings, name='profile-security-settings'),
    # path('user-settings/<slug:profile>/account', views.profileAccountSettings, name='profile-account-settings'),
]

# tutor settings link
urlpatterns += [
    # path('user-settings/', views.userSettings, name='user-settings'),
    # path('user-settings/tutor/biography', views.tutorBiographySettings, name='tutor-biography-settings'),
    # path('user-settings/tutor/notification', views.tutorNotificationSettings, name='tutor-notification-settings'),
]

# student settings link
urlpatterns += [
    # path('user-settings/tutor/biography', views.studentBiographySettings, name='student-biography-settings'),
    # path('user-settings/student/notification', views.studentNotificationSettings, name='student-notification-settings'),
]

# parent settings link
urlpatterns += [
    # path('user-settings/parent/notification', views.tutorNotificationSettings, name='parent-notification-settings'),
]

# footer links
urlpatterns += [
    path('get-in-touch/', views.getInTouch, name='get-in-touch'),
    path('ourFeatures/', views.ourFeatures, name='ourFeatures'),
]

# api
urlpatterns += [
    path(
        'api/v1/requestDeleteCodeApiEventVersion1Component',
        RequestDeleteCodeApiEventVersion1Component.as_view(),
        name='requestDeleteCodeApiEventVersion1Component'
    ),
    path(
        'api/v1/cookieConsentApiEventVersion1Component',
        CookieConsentApiEventVersion1Component.as_view(),
        name='cookieConsentApiEventVersion1Component'
    ),
]
