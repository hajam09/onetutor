from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests import userDataHelper
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountProfileSecuritySettingsViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountProfileSecuritySettingsViewTest, self).setUp(
            reverse('accounts:profile-security-settings', kwargs={'profile': 'tutor'})
        )
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        userDataHelper.createTutorProfileForUser(self.user)

    def testProfileSecuritySettingsGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/tutor/profileSecuritySettings.html')

    def testPasswordUpdatedSuccessfully(self):
        testParams = self.TestParams(TEST_PASSWORD, 'PassWord2022', 'PassWord2022')
        response = self.post(testParams.getData())

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('PassWord2022'))
        self.assertNotEqual(response.context['form'], None)

    def testPasswordNotUpdated(self):
        testParams = self.TestParams(TEST_PASSWORD, '1', '1')
        response = self.post(testParams.getData())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.check_password(TEST_PASSWORD))
        self.assertNotEqual(response.context['form'], None)


    class TestParams:

        def __init__(self, currentPassword, newPassword, repeatNewPassword):
            self.currentPassword = currentPassword
            self.newPassword = newPassword
            self.repeatNewPassword = repeatNewPassword

        def getData(self):
            data = {
                'currentPassword': self.currentPassword,
                'newPassword': self.newPassword,
                'repeatNewPassword': self.repeatNewPassword,
            }
            return data
