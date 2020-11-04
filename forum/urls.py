from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('<slug:page_number>/', views.mainpage, name='mainpage'),
	path('community/<slug:forum_url>/<slug:page_number>/', views.parentforumpage, name='parentforumpage'),
	path('vote/upvote_sub_forum/', views.upvote_sub_forum, name='upvote_sub_forum'),
	path('vote/downvote_sub_forum/', views.downvote_sub_forum, name='downvote_sub_forum'),
]