from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from onetutor.operations import emailOperations


class RequestDeleteCodeApiEventVersion1Component(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not request.session.session_key:
            request.session.save()

        emailOperations.sendEmailForAccountDeleteCode(self.request, self.request.user)

        response = {
            'success': True,
            'message': 'Check your email for the code.'
        }
        return Response(response, status=status.HTTP_200_OK)
