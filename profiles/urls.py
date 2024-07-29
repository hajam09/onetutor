from django.urls import path

from profiles.views import (
    CreateProfileTemplateView,
    SettingsTemplateView
)

app_name = 'profiles'

urlpatterns = [
    path('create-profile/', CreateProfileTemplateView.as_view(), name='create-profile-view'),
    path('settings/', SettingsTemplateView.as_view(), name='settings-view'),
]
