from unittest import skip
from unittest.mock import patch

from accounts.forms import LoginForm
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTest import BaseTest


class LoginFormFormTest(BaseTest):

    def setUp(self) -> None:
        super(LoginFormFormTest, self).setUp('')

    # @skip
    @patch('accounts.forms.login')
    def testFormIsValid(self, mockLogin):
        mockLogin.return_value = True
        testParams = self.TestParams(email=self.user.email, password=TEST_PASSWORD, rememberMe='on')
        form = LoginForm(request=self.request, data=testParams.getData())
        self.assertTrue(form.is_valid())
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def testFormIncorrectCredentials(self):
        testParams = self.TestParams(email=self.user.email, password='TEST_PASSWORD', rememberMe='on')
        form = LoginForm(request=self.request, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertNotIn('_auth_user_id', self.client.session)

        for message in form.errors.as_data()['password'][0]:
            self.assertEquals(message, 'Username or Password did not match! ')

    class TestParams:

        def __init__(self, email, password, rememberMe):
            self.email = email
            self.password = password
            self.rememberMe = rememberMe

        def getData(self):
            data = {
                'email': self.email,
                'password': self.password,
                'rememberMe': self.rememberMe
            }
            return data
