from http import HTTPStatus

from django.http import QueryDict, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from jira2.models import Board


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
