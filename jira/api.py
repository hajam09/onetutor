from http import HTTPStatus

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from jira.models import Ticket


@method_decorator(csrf_exempt, name='dispatch')
class TicketObjectDetailsApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        tickets = Ticket.objects.all().select_related("subTask")

        response = {
            "success": True,
            "data": {
                "tickets": [
                    {
                        "id": ticket.id,
                        "internalKey": ticket.url,
                        "project": ticket.project,
                        "summary": ticket.summary,
                        "issueType": ticket.issueType,
                        "description": ticket.description,
                        "storyPoints": ticket.points,
                        "createdDate": ticket.createdDate,
                        "priority": ticket.priority,
                        "subTask": [i.id for i in ticket.subTask.all()],

                    } for ticket in tickets
                ]
            }
        }
        return JsonResponse(response, status=HTTPStatus.OK)
