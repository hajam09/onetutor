from django.urls import path

from profiles.views import (
    CreateProfileTemplateViewApi,
)

app_name = 'profiles'

urlpatterns = [
    path('create-profile/', CreateProfileTemplateViewApi.as_view(), name='create-profile-view'),
]
