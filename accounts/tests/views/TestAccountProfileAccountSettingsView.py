from django.contrib.auth.models import User
from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountProfileAccountSettingsViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountProfileAccountSettingsViewTest, self).setUp(
            reverse('accounts:profile-account-settings', kwargs={'profile': 'tutor'})
        )
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testProfileAccountSettingsGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/tutor/profileAccountSettings.html')

    def testDeleteAccountWithCorrectCode(self):
        testParams = self.TestParams()
        response = self.post(testParams.getDeletePayload(self.getSessionKey()))
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/')
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
        # with self.assertRaises(User.DoesNotExist):
        #     User.objects.get(id=self.user.id)

        for message in messages:
            self.assertEqual(
                str(message),
                'Account deleted successfully'
            )

    def testDeleteAccountWithIncorrectCode(self):
        testParams = self.TestParams()
        response = self.post(testParams.getDeletePayload(''))
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

        for message in messages:
            self.assertEqual(
                str(message),
                'Account delete code is incorrect, please try again later.'
            )


    class TestParams:

        def getDeletePayload(self, code):
            data = {
                'deleteAccount': '',
                'delete-code': code,
            }
            return data
