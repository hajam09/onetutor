from django.urls import path, include
from chat import views
app_name = "chat"

urlpatterns = [
	path('', views.chatpage, name='chatpage'),
]