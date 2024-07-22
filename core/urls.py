from django.urls import path

from core.views import (
    indexView
)

app_name = 'core'

urlpatterns = [
    path('', indexView, name='index-view'),
]
