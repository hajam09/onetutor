from datetime import datetime

from django.urls import reverse

from dashboard.models import UserLogin
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountLogoutViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountLogoutViewTest, self).setUp(reverse('accounts:logout'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        self.userLogin = UserLogin.objects.create(user=self.request.user)

    def testLogoutUser(self):
        response = self.get()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(self.userLogin.loginTime.date(), datetime.now().date())
