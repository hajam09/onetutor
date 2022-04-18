from django.urls import reverse

from onetutor.tests.BaseTestViews import BaseTestViews


class AccountLoginViewTest(BaseTestViews):
    """
        Testing the login view where the user want to login to the system, and it's subsidiary function.
    """

    def setUp(self) -> None:
        super(AccountLoginViewTest, self).setUp(reverse('accounts:login'))
        # self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testLoginGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
