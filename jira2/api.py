from http import HTTPStatus

from django.core.cache import cache
from django.http import QueryDict, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from jira2.models import Board, Column, Label, Ticket, Project
from onetutor.operations import databaseOperations


@method_decorator(csrf_exempt, name='dispatch')
class BoardSettingsViewGeneralDetailsApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        boardUrl = self.kwargs.get("boardUrl", None)
        put = QueryDict(self.request.body)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        boardName = put.get("board-name", board.name)
        boardProjects = put.getlist("board-projects[]", [])
        boardAdmins = put.getlist("board-admins[]", [])
        boardMembers = put.getlist("board-members[]", [])
        boardVisibility = put.get("board-visibility", board.isPrivate)

        board.name = boardName
        board.isPrivate = boardVisibility == 'visibility-members'

        # just passing the ids will do the job
        board.projects.clear()
        board.projects.add(*boardProjects)

        board.admins.clear()
        board.admins.add(*boardAdmins)

        board.members.clear()
        board.members.add(*boardMembers)

        board.save()

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class BoardSettingsViewBoardColumnsApiEventVersion1Component(View):

    def post(self, *args, **kwargs):
        boardUrl = self.kwargs.get("boardUrl", None)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        newColumnName = self.request.POST.get("column-name", None)

        if newColumnName is not None:
            boardColumns = board.boardColumns.all()

            existingColumn = [i for i in boardColumns if i.name.lower() == newColumnName.lower()]
            if len(existingColumn) == 0:
                newColumn = Column.objects.create(
                    board=board,
                    name=newColumnName,
                    orderNo=board.boardColumns.count() + 1
                )
                response = {
                    "success": True,
                    "data": {
                        "id": newColumn.id,
                        "name": newColumn.name,
                        "orderNo": newColumn.orderNo
                    }
                }
                return JsonResponse(response, status=HTTPStatus.OK)
        return JsonResponse({}, status=HTTPStatus.ACCEPTED)

    def put(self, *args, **kwargs):
        boardUrl = self.kwargs.get("boardUrl", None)
        put = QueryDict(self.request.body)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        columnId = put.get("column-id", None)
        column = databaseOperations.getObjectByIdOrNone(board.boardColumns.all(), columnId)
        if column is None:
            response = {
                "success": False,
                "message": "Could not update the column name."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        columnName = put.get("column-name", column.name)
        column.name = columnName
        column.save(update_fields=["name"])

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def delete(self, *args, **kwargs):
        # Just for this board settings view, the boardUrl is required.
        # In other API's only the column ID will be needed.
        boardUrl = self.kwargs.get("boardUrl", None)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        put = QueryDict(self.request.body)
        columnId = put.get("column-id", None)

        # TODO: Before removing columns check if there are any ticket present in this column. see TutorProfileForm
        Column.objects.filter(id=columnId).delete()

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class BoardColumnsBulkOrderChangeApiEventVersion1Component(View):

    def put(self, *args, **kwargs):
        # Just for this board settings view, the boardUrl is required.
        # In other API's only the column Id and their order are required.
        boardUrl = self.kwargs.get("boardUrl", None)
        put = QueryDict(self.request.body)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        newColumnOrder = put.getlist('new-column-order[]', None)

        if len(newColumnOrder) > 0:
            newColumnOrder = [int(i.split('-')[2]) for i in newColumnOrder]
            for i in board.boardColumns.all():
                i.orderNo = newColumnOrder.index(i.pk)
                i.save(update_fields=['orderNo'])

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class BoardSettingsViewBoardLabelsApiEventVersion1Component(View):

    def post(self, *args, **kwargs):
        boardUrl = self.kwargs.get("boardUrl", None)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        newLabelName = self.request.POST.get("label-name", None)

        if newLabelName is None:
            return JsonResponse({}, status=HTTPStatus.ACCEPTED)

        newLabel = Label.objects.create(
            board=board,
            name=newLabelName,
        )
        response = {
            "success": True,
            "data": {
                "id": newLabel.id,
                "name": newLabel.name,
                "colour": newLabel.colour,
                "orderNo": newLabel.orderNo
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def put(self, *args, **kwargs):
        boardUrl = self.kwargs.get("boardUrl", None)
        put = QueryDict(self.request.body)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        labelId = put.get("label-id", None)
        label = databaseOperations.getObjectByIdOrNone(board.boardLabels.all(), labelId)
        if label is None:
            response = {
                "success": False,
                "message": "Could not update the label name."
            }
            return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)

        labelName = put.get("label-name", label.name)
        labelColour = put.get("label-colour", label.colour)

        updateFields = ['name', 'colour']
        label.name = labelName
        label.colour = labelColour
        label.save(update_fields=updateFields)

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)

    def delete(self, *args, **kwargs):
        # Just for this board settings view, the boardUrl is required.
        # In other API's only the label ID will be needed.
        boardUrl = self.kwargs.get("boardUrl", None)

        try:
            board = Board.objects.get(url=boardUrl)
        except Board.DoesNotExist:
            response = {
                "success": False,
                "message": "Could not find a board with url/id: ".format(boardUrl)
            }
            return JsonResponse(response, status=HTTPStatus.NOT_FOUND)

        put = QueryDict(self.request.body)
        labelId = put.get("label-id", None)

        Label.objects.filter(id=labelId, board=board).delete()

        response = {
            "success": True
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class TicketObjectForSubTasksInStandardTicketApiEventVersion1Component(View):

    def post(self, *args, **kwargs):
        projectId = self.request.POST.get("project-id", None)
        ticketSummary = self.request.POST.get("ticket-summary", None)
        standardTicketId = self.request.POST.get("ticket-id", None)

        ticketIssueTypeComponents = cache.get("ticketIssueTypeComponents")
        ticketSecurityComponents = cache.get("ticketSecurityComponents")
        ticketPriorityComponents = cache.get("ticketPriorityComponents")

        project = Project.objects.get(id=projectId)
        newTicketNumber = project.projectTickets.count() + 1

        ticket = Ticket()
        ticket.internalKey = project.code + "-" + str(newTicketNumber)
        ticket.summary = ticketSummary
        ticket.project = project
        ticket.reporter = self.request.user
        ticket.issueType = next((i for i in ticketIssueTypeComponents if i.code == "SUB_TASK"), None)
        ticket.securityLevel = next((i for i in ticketSecurityComponents if i.code == "INTERNAL"), None)
        ticket.priority = next((i for i in ticketPriorityComponents if i.code == "MEDIUM"), None)

        if standardTicketId is not None:
            standardTicket = Ticket.objects.get(id=standardTicketId)
            ticket.sprint = standardTicket.sprint
            ticket.status = standardTicket.status
            ticket.board = standardTicket.board
            ticket.column = standardTicket.column

            ticket.save()
            standardTicket.subTask.add(ticket)

            response = {
                "success": True,
                "data": {
                    "id": ticket.id,
                    "internalKey": ticket.internalKey,
                    "summary": ticket.summary,
                    "link": "/jira2/ticket/" + str(ticket.internalKey),
                    "issueType": {
                        "internalKey": ticket.issueType.internalKey,
                        "icon": "/static/" + ticket.issueType.icon,
                    },
                    "priority": {
                        "internalKey": ticket.priority.internalKey,
                        "icon": "/static/" + ticket.priority.icon
                    },
                }
            }
            return JsonResponse(response, status=HTTPStatus.OK)

        response = {
            "success": False,
            "message": "Unable to create a subtask."
        }
        return JsonResponse(response, status=HTTPStatus.BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TicketObjectForIssuesInTheEpicTicketApiEventVersion1Component(View):

    def post(self, *args, **kwargs):
        projectId = self.request.POST.get("project-id", None)
        ticketSummary = self.request.POST.get("ticket-summary", None)
        issueType = self.request.POST.get("issue-type", None)
        epicTicketId = self.request.POST.get("epic-ticket-id", None)

        ticketIssueTypeComponents = cache.get("ticketIssueTypeComponents")
        ticketSecurityComponents = cache.get("ticketSecurityComponents")
        ticketStatusComponents = cache.get("ticketStatusComponents")
        ticketPriorityComponents = cache.get("ticketPriorityComponents")

        project = Project.objects.get(id=projectId)
        newTicketNumber = project.projectTickets.count() + 1

        ticket = Ticket()
        ticket.internalKey = project.code + "-" + str(newTicketNumber)
        ticket.summary = ticketSummary
        ticket.project = project
        ticket.reporter = self.request.user
        ticket.issueType = next((i for i in ticketIssueTypeComponents if i.code == issueType), None)
        ticket.securityLevel = next((i for i in ticketSecurityComponents if i.code == "EXTERNAL"), None)
        ticket.status = next((i for i in ticketStatusComponents if i.code == "BACKLOG"), None)
        ticket.priority = next((i for i in ticketPriorityComponents if i.code == "MEDIUM"), None)

        if epicTicketId is not None:
            epicTicket = Ticket.objects.get(id=epicTicketId, issueType__code="EPIC")
            ticket.board = epicTicket.board
            ticket.column = epicTicket.column
            ticket.epic = epicTicket

        ticket.save()

        response = {
            "success": True,
            "data": {
                "id": ticket.id,
                "internalKey": ticket.internalKey,
                "summary": ticket.summary,
                "link": "/jira2/ticket/" + str(ticket.internalKey),
                "issueType": {
                    "internalKey": ticket.issueType.internalKey,
                    "icon": "/static/" + ticket.issueType.icon,
                },
                "priority": {
                    "internalKey": ticket.priority.internalKey,
                    "icon": "/static/" + ticket.priority.icon
                },
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)
