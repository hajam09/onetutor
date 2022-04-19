import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests import userDataHelper
from onetutor.tests.BaseTestAjax import BaseTestAjax


class RequestCopyOfDataViewTest(BaseTestAjax):

    def setUp(self) -> None:
        super(RequestCopyOfDataViewTest, self).setUp(reverse('accounts:requestCopyOfData'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testUserNotAuthenticated(self):
        self.client.logout()
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(ajaxResponse["statusCode"], HTTPStatus.BAD_REQUEST)
        self.assertEquals(ajaxResponse["message"], 'Login to request your data.')

    @patch('onetutor.operations.generalOperations.getTutorRequestedStoredData')
    @patch('onetutor.operations.emailOperations.sendTutorRequestedStoredData')
    def testTutorProfile(self, mockGetTutorRequestedStoredData, mockSendTutorRequestedStoredData):
        userDataHelper.createTutorProfileForUser(self.user)
        response = self.get()
        ajaxResponse = json.loads(response.content)

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertEquals(ajaxResponse["statusCode"], HTTPStatus.OK)
        self.assertEquals(ajaxResponse["message"], 'A copy is sent to your email.')

        mockGetTutorRequestedStoredData.assert_called_once()
        mockSendTutorRequestedStoredData.assert_called_once()

    def testStudentProfile(self):
        # TODO
        pass

    def testParentProfile(self):
        # TODO
        pass
