from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	path('viewforum/<slug:forum_url>/', views.forumpage, name='forumpage'),
	path('upvote_sub_forum/', views.upvote_sub_forum, name='upvote_sub_forum'),
	path('downvote_sub_forum/', views.downvote_sub_forum, name='downvote_sub_forum'),
]