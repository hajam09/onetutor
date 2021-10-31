from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('c/<slug:communityUrl>/', views.communityPage, name='communityPage'),
    path('c/<slug:communityUrl>/f/<slug:forumUrl>', views.forumPage, name='forumPage'),

    path('api/v1/communityOperations/<slug:communityId>', views.communityOperationsAPI, name='communityOperationsAPI'),
    path('api/v1/forumOperations/<slug:forumId>', views.forumOperationsAPI, name='forumOperationsAPI'),
    path('api/v1/forumCommentOperations/<slug:commentId>', views.forumCommentOperationsAPI, name='forumCommentOperationsAPI'),
]