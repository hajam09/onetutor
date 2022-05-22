from django.urls import path

from jira2 import views
from jira2.api import BoardColumnsBulkOrderChangeApiEventVersion1Component
from jira2.api import BoardSettingsViewBoardColumnsApiEventVersion1Component
from jira2.api import BoardSettingsViewBoardLabelsApiEventVersion1Component
from jira2.api import BoardSettingsViewGeneralDetailsApiEventVersion1Component

app_name = "jira2"

urlpatterns = [
    # path('', views.mainPage, name='main-page'),
    # path('sprint-board/', views.sprintBoard, name='sprintBoard'),
    # path('back-log/', views.backLog, name='backLog'),
    path('ticket/<slug:internalKey>/', views.ticketPage, name='ticket-page'),
    path('projects/', views.projects, name='projects-page'),
    path('project/<slug:url>/', views.project, name='project-page'),
    path('project/<slug:url>/settings', views.projectSettings, name='project-settings'),
    path('boards/', views.boards, name='boards-page'),
    path('board/<slug:url>/', views.board, name='board-page'),
    path('board/<slug:url>/settings/', views.boardSettings, name='board-settings'),
]

# api
urlpatterns += [
    path(
        'tutoring/api/v1/boardSettingsViewGeneralDetailsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewGeneralDetailsApiEventVersion1Component.as_view(),
        name='boardSettingsViewGeneralDetailsApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/boardSettingsViewBoardColumnsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewBoardColumnsApiEventVersion1Component.as_view(),
        name='boardSettingsViewBoardColumnsApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/boardColumnsBulkOrderChangeApiEventVersion1Component/<slug:boardUrl>',
        BoardColumnsBulkOrderChangeApiEventVersion1Component.as_view(),
        name='boardColumnsBulkOrderChangeApiEventVersion1Component'
    ),
    path(
        'tutoring/api/v1/boardSettingsViewBoardLabelsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewBoardLabelsApiEventVersion1Component.as_view(),
        name='boardSettingsViewBoardLabelsApiEventVersion1Component'
    ),
]
