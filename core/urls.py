from django.urls import path

from core.views import (
    indexView,
    StaticPageView
)

app_name = 'core'

urlpatterns = [
    path('', indexView, name='index-view'),
    path('<str:pageName>/', StaticPageView.as_view(), name='static-page'),
]
