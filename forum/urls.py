from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('<slug:forum_url>/', views.forumpage, name='forumpage'),
	# path('like_sub_forum/', views.like_sub_forum, name='like_sub_forum'),
	# path('dislike_sub_forum/', views.dislike_sub_forum, name='dislike_sub_forum'),
]