from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
	path('', views.mainpage, name='mainpage'),
	# path('community/<slug:community_url>/<slug:page_number>/', views.communitypage, name='communitypage'),
	# path('vote/upvote_community/', views.upvote_community, name='upvote_community'),
	# path('vote/downvote_community/', views.downvote_community, name='downvote_community'),
	# path('vote/upvote_forum/', views.upvote_forum, name='upvote_forum'),
	# path('vote/downvote_forum/', views.downvote_forum, name='downvote_forum'),
]