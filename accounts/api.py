from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from onetutor.utils import emailOperations


class CookieConsentApiEventVersion1Component(APIView):

    def put(self, request, *args, **kwargs):
        if not self.request.session.session_key:
            self.request.session.save()

        response = {
            'success': True,
        }
        return Response(response, status=status.HTTP_200_OK)


class RequestDeleteCodeApiEventVersion1Component(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        emailOperations.sendEmailForAccountDeleteCode(self.request, self.request.user)

        response = {
            'success': True,
            'message': 'Check your email for the code.'
        }
        return Response(response, status=status.HTTP_200_OK)
