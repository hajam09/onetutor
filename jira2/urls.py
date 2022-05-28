from django.urls import path

from jira2 import views
from jira2.api import BoardColumnsBulkOrderChangeApiEventVersion1Component
from jira2.api import BoardObjectDetailsApiEventVersion1Component
from jira2.api import BoardSettingsViewBoardColumnsApiEventVersion1Component
from jira2.api import BoardSettingsViewBoardLabelsApiEventVersion1Component
from jira2.api import BoardSettingsViewGeneralDetailsApiEventVersion1Component
from jira2.api import KanbanBoardBacklogActiveTicketsApiEventVersion1Component
from jira2.api import KanbanBoardBacklogInActiveTicketsApiEventVersion1Component
from jira2.api import KanbanBoardDetailsAndItemsApiEventVersion1Component
from jira2.api import KanbanBoardTicketColumnUpdateApiEventVersion1Component
from jira2.api import TicketObjectBaseDataUpdateApiEventVersion1Component
from jira2.api import TicketObjectBulkCreateApiEventVersion1Component
from jira2.api import TicketObjectForIssuesInTheEpicTicketApiEventVersion1Component
from jira2.api import TicketObjectForSubTasksInStandardTicketApiEventVersion1Component

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
    path('kanbanBoard/<slug:url>/', views.kanbanBoard, name='kanban-board-page'),
    path('board/<slug:url>/settings/', views.boardSettings, name='board-settings'),
    path('board/<slug:url>/backlog/', views.backlog, name='board-backlog'),
    path('people/team/<slug:url>/', views.team, name='team-settings'),
]

# api
urlpatterns += [
    path(
        'api/v1/boardSettingsViewGeneralDetailsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewGeneralDetailsApiEventVersion1Component.as_view(),
        name='boardSettingsViewGeneralDetailsApiEventVersion1Component'
    ),
    path(
        'api/v1/boardSettingsViewBoardColumnsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewBoardColumnsApiEventVersion1Component.as_view(),
        name='boardSettingsViewBoardColumnsApiEventVersion1Component'
    ),
    path(
        'api/v1/boardColumnsBulkOrderChangeApiEventVersion1Component/<slug:boardUrl>',
        BoardColumnsBulkOrderChangeApiEventVersion1Component.as_view(),
        name='boardColumnsBulkOrderChangeApiEventVersion1Component'
    ),
    path(
        'api/v1/boardSettingsViewBoardLabelsApiEventVersion1Component/<slug:boardUrl>',
        BoardSettingsViewBoardLabelsApiEventVersion1Component.as_view(),
        name='boardSettingsViewBoardLabelsApiEventVersion1Component'
    ),
    path(
        'api/v1/ticketObjectForIssuesInTheEpicTicketApiEventVersion1Component',
        TicketObjectForIssuesInTheEpicTicketApiEventVersion1Component.as_view(),
        name='ticketObjectForIssuesInTheEpicTicketApiEventVersion1Component'
    ),
    path(
        'api/v1/ticketObjectForSubTasksInStandardTicketApiEventVersion1Component',
        TicketObjectForSubTasksInStandardTicketApiEventVersion1Component.as_view(),
        name='ticketObjectForSubTasksInStandardTicketApiEventVersion1Component'
    ),
    path(
        'api/v1/ticketObjectBaseDataUpdateApiEventVersion1Component/<int:ticketId>',
        TicketObjectBaseDataUpdateApiEventVersion1Component.as_view(),
        name='ticketObjectBaseDataUpdateApiEventVersion1Component'
    ),
    path(
        'jira2/api/v1/kanbanBoardDetailsAndItemsApiEventVersion1Component/<int:boardId>',
        KanbanBoardDetailsAndItemsApiEventVersion1Component.as_view(),
        name='kanbanBoardDetailsAndItemsApiEventVersion1Component'
    ),
    path(
        'api/v1/kanbanBoardTicketColumnUpdateApiEventVersion1Component',
        KanbanBoardTicketColumnUpdateApiEventVersion1Component.as_view(),
        name='kanbanBoardTicketColumnUpdateApiEventVersion1Component'
    ),
    path(
        'api/v1/kanbanBoardBacklogInActiveTicketsApiEventVersion1Component/<int:boardId>',
        KanbanBoardBacklogInActiveTicketsApiEventVersion1Component.as_view(),
        name='kanbanBoardBacklogInActiveTicketsApiEventVersion1Component'
    ),
    path(
        'api/v1/kanbanBoardBacklogActiveTicketsApiEventVersion1Component/<int:boardId>',
        KanbanBoardBacklogActiveTicketsApiEventVersion1Component.as_view(),
        name='kanbanBoardBacklogActiveTicketsApiEventVersion1Component'
    ),
    path(
        'api/v1/boardObjectDetailsApiEventVersion1Component/<int:boardId>',
        BoardObjectDetailsApiEventVersion1Component.as_view(),
        name='boardObjectDetailsApiEventVersion1Component'
    ),
    path(
        'api/v1/ticketObjectBulkCreateApiEventVersion1Component',
        TicketObjectBulkCreateApiEventVersion1Component.as_view(),
        name='ticketObjectBulkCreateApiEventVersion1Component'
    ),
]
