from datetime import datetime
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from dashboard.models import UserSession, UserLogin
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountLoginViewTest(BaseTestViews):
    """
        Testing the login view where the user want to login to the system, and it's subsidiary function.
    """

    def setUp(self) -> None:
        super(AccountLoginViewTest, self).setUp(reverse('accounts:login'))

    def testLoginGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def testLoginAuthenticateValidUser(self):
        testParams = self.TestParams(self.user.username, TEST_PASSWORD)
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        response = self.post(testParams.getData())

        sessionKey = self.getSessionKey()
        userSession = UserSession.objects.filter(user=self.user).last()
        userLogin = UserLogin.objects.filter(user=self.user).last()

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/')
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

        self.assertEqual(cache.get(sessionKey), None)
        self.assertEqual(userSession.sessionKey, sessionKey)
        self.assertEqual(userSession.dateTime.date(), datetime.now().date())
        self.assertEqual(userLogin.loginTime.date(), datetime.now().date())

    @patch('accounts.views.LoginForm.is_valid')
    def testLoginAuthenticateInvalidUser(self, mockLoginForm):
        mockLoginForm.return_value = False
        testParams = self.TestParams(self.user.username, 'TEST_PASSWORD')
        response = self.post(testParams.getData())

        sessionKey = self.getSessionKey()
        userSession = UserSession.objects.filter(user=self.user).last()
        userLogin = UserLogin.objects.filter(user=self.user).last()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertNotIn('_auth_user_id', self.client.session)

        self.assertEqual(cache.get(sessionKey), 1)
        self.assertEqual(userSession, None)
        self.assertEqual(userLogin, None)
        # self.assertIn(response.context, "form")

    def testLoginMaxAttempts(self):
        for i in range(6):
            response = self.post()

        self.assertNotEqual(cache.get(self.getSessionKey()), None)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/')

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)

        for message in messages:
            self.assertEqual(
                str(message),
                'Your account has been temporarily locked out because of too many failed login attempts.'
            )
        cache.set(self.getSessionKey(), None)

    class TestParams:

        def __init__(self, email, password):
            self.email = email
            self.password = password

        def getData(self):
            data = {
                'email': self.email,
                'password': self.password,
            }
            return data
