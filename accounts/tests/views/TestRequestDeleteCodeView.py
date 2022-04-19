import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestAjax import BaseTestAjax


class RequestDeleteCodeViewTest(BaseTestAjax):

    def setUp(self) -> None:
        super(RequestDeleteCodeViewTest, self).setUp(reverse('accounts:requestDeleteCode'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testUserNotAuthenticated(self):
        self.client.logout()
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(ajaxResponse["statusCode"], HTTPStatus.BAD_REQUEST)
        self.assertEquals(ajaxResponse["message"], 'Login to request a code.')

    @patch('onetutor.operations.emailOperations.sendEmailForAccountDeletionCode')
    def testEmailSentSuccessfully(self, mockSendEmailForAccountDeletionCode):
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(ajaxResponse["statusCode"], HTTPStatus.OK)
        self.assertEquals(ajaxResponse["message"], 'Check your email for the code.')

        mockSendEmailForAccountDeletionCode.assert_called_once()
