from django.urls import path

from chat import views

app_name = "chat"

urlpatterns = [
    path('', views.chatPage, name='chatPage'),
]
