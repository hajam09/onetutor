import json
from datetime import datetime

from django.urls import reverse

from accounts.models import UserSession
from onetutor.tests.BaseTestAjax import BaseTestAjax


class AccountCookieConsentViewTest(BaseTestAjax):

    def setUp(self) -> None:
        super(AccountCookieConsentViewTest, self).setUp(reverse('accounts:cookieConsent'))

    def testConsentStageAsked(self):
        testParams = self.TestParams('ASKED')
        response = self.get(testParams.getStage())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertTrue(ajaxResponse["askConsent"])

    def testConsentStageConfirmed(self):
        testParams = self.TestParams('CONFIRMED')
        response = self.get(testParams.getStage())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertFalse(ajaxResponse["askConsent"])

        userSession = UserSession.objects.filter(sessionKey=self.getSessionKey()).last()
        self.assertEqual(userSession.dateTime.date(), datetime.now().date())
        self.assertEqual(userSession.user, None)

    def testConsentStageRejected(self):
        testParams = self.TestParams('REJECTED')
        response = self.get(testParams.getStage())
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(ajaxResponse["statusCode"], 200)
        self.assertFalse(ajaxResponse["askConsent"])

    class TestParams:

        def __init__(self, stage):
            self.stage = stage

        def getStage(self):
            payload = {
                'consentStage': self.stage
            }
            return payload
