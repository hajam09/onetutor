from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('viewforum/<slug:forum_url>/', views.forumpage, name='forumpage'),
]