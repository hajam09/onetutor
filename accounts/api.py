from http import HTTPStatus

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from accounts.models import TutorProfile, StudentProfile, ParentProfile
from onetutor.operations import emailOperations, generalOperations
from onetutor.utils.exception.ProfileNotFoundException import ProfileNotFoundException


class RequestCopyOfDataApiEventVersion1Component(View):
    # TODO: Parent can request data for all their children.

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            response = {
                "success": False,
                "message": "Login to request information."
            }
            return JsonResponse(response, status=HTTPStatus.UNAUTHORIZED)

        profile = generalOperations.getProfileForUser(self.request.user)

        if isinstance(profile, TutorProfile):
            pass
        elif isinstance(profile, StudentProfile):
            pass
        elif isinstance(profile, ParentProfile):
            pass
        else:
            raise ProfileNotFoundException(self.request.user)

        response = {
            "success": True,
            "message": "A copy of your data is sent to your email."
        }
        return JsonResponse(response, status=HTTPStatus.OK)


class RequestDeleteCodeApiEventVersion1Component(View):

    def get(self, *args, **kwargs):

        if not self.request.user.is_authenticated:
            response = {
                "success": False,
                "message": "Login to request a code."
            }
            return JsonResponse(response, status=HTTPStatus.UNAUTHORIZED)

        if not self.request.session.session_key:
            self.request.session.save()

        emailOperations.sendEmailForAccountDeletionCode(self.request, self.request.user)

        response = {
            "success": True,
            "message": "Check your email for the code."
        }
        return JsonResponse(response, status=HTTPStatus.OK)


@method_decorator(csrf_exempt, name='dispatch')
class CookieConsentApiEventVersion1Component(View):

    def get(self, *args, **kwargs):
        if not self.request.session.session_key:
            self.request.session.save()

        consentStage = self.request.GET.get('consentStage')

        # if consentStage == "ASKED":
        #     askConsent = not (UserSession.objects.filter(
        #         sessionKey=self.request.session.session_key).exists() or self.request.user.is_authenticated)
        #
        # elif consentStage == "CONFIRMED":
        #     user = None if isinstance(self.request.user, AnonymousUser) else self.request.user
        #     UserSession.objects.create(
        #         user=user,
        #         ipAddress=generalOperations.getClientInternetProtocolAddress(self.request),
        #         userAgent=self.request.META['HTTP_USER_AGENT'],
        #         sessionKey=self.request.session.session_key
        #     )
        #     askConsent = False
        # elif consentStage == "REJECTED":
        #     askConsent = False
        # else:
        #     response = {
        #         "message": "Unexpected consent stage"
        #     }
        #     return JsonResponse(response, status=HTTPStatus.FORBIDDEN)

        response = {
            "askConsent": "askConsent"
        }
        return JsonResponse(response, status=HTTPStatus.OK)
