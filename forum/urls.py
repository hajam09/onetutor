from django.urls import path

from forum.views import (
    indexView,
    postView
)

app_name = 'forum'

urlpatterns = [
    path('', indexView, name='index-view'),
    path('posts/<int:id>/', postView, name='post-view'),
]
