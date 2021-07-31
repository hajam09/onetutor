from django.urls import path, include
from forum import views
app_name = "forum"

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('c/<slug:communityUrl>/', views.communityPage, name='communityPage'),
    path('c/<slug:communityUrl>/f/<slug:forumUrl>', views.forumPage, name='forumPage'),
]