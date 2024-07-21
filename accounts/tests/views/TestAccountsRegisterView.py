from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountRegisterViewTest(BaseTestViews):
    """
    	Testing the register view where the user want to create an account.
    """

    def setUp(self) -> None:
        super(AccountRegisterViewTest, self).setUp(reverse('accounts:register-view'))

    def testRegisterGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registrationView.html')

    @patch('onetutor.operations.emailOperations.sendEmailToActivateAccount')
    def testRegisterAccountSuccess(self, mockSendEmailToActivateAccount):
        testParams = self.TestParams(
            'example@example.com', 'example@example.com', TEST_PASSWORD, TEST_PASSWORD, 'example', 'example'
        )

        response = self.post(testParams.getData())
        messages = list(response.context['messages'])

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/')
        self.assertTrue(User.objects.filter(username='example@example.com').exists())
        self.assertEqual(len(messages), 1)

        for message in messages:
            self.assertEqual(
                str(message),
                'We\'ve sent you an activation link. Please check your email.'
            )

        mockSendEmailToActivateAccount.assert_called_once()

    @patch('accounts.views.RegistrationForm.is_valid')
    def testRegisterAccountFailed(self, mockRegistrationForm):
        mockRegistrationForm.return_value = False

        testParams = self.TestParams(
            self.user.username, self.user.email, TEST_PASSWORD, TEST_PASSWORD, self.user.first_name, self.user.last_name
        )

        response = self.post(testParams.getData())
        self.assertNotEqual(response.context['form'], None)

    class TestParams:

        def __init__(self, username, email, password1, password2, first_name, last_name):
            self.username = username
            self.email = email
            self.password1 = password1
            self.password2 = password2
            self.first_name = first_name
            self.last_name = last_name

        def getData(self):
            data = {
                'username': self.username,
                'email': self.email,
                'password1': self.password1,
                'password2': self.password2,
                'first_name': self.first_name,
                'last_name': self.last_name,
            }
            return data
