from unittest.mock import patch

from django.urls import reverse

from onetutor.tests.BaseTestViews import BaseTestViews


class AccountPasswordRequestViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountPasswordRequestViewTest, self).setUp(reverse('accounts:password-request'))

    def testPasswordRequestGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/passwordResetRequestView.html')

    @patch('onetutor.operations.emailOperations.sendEmailToChangePassword')
    def testPasswordRequestExistingUser(self, mockSendEmailToChangePassword):
        testParams = self.TestParams(self.user.email)
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        for message in messages:
            self.assertEqual(
                str(message),
                'Check your email for a password change link.'
            )

        mockSendEmailToChangePassword.assert_called_once()

    @patch('onetutor.operations.emailOperations.sendEmailToChangePassword')
    def testPasswordRequestNonExistingUser(self, mockSendEmailToChangePassword):
        testParams = self.TestParams("example@example.com")
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        for message in messages:
            self.assertEqual(
                str(message),
                'Check your email for a password change link.'
            )

        mockSendEmailToChangePassword.assert_not_called()

    class TestParams:

        def __init__(self, email):
            self.email = email

        def getData(self):
            data = {
                'email': self.email,
            }
            return data
