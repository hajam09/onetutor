from accounts.forms import UserSettingsPasswordUpdateForm
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTest import BaseTest

@skip('')
class UserSettingsPasswordUpdateFormTest(BaseTest):

    def setUp(self) -> None:
        super(UserSettingsPasswordUpdateFormTest, self).setUp('')
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testFormIsValid(self):
        testParams = self.TestParams(newPassword='RaNdOmPaSsWoRd56', repeatNewPassword='RaNdOmPaSsWoRd56')
        form = UserSettingsPasswordUpdateForm(request=self.request, data=testParams.getData())
        self.assertTrue(form.is_valid())
        form.updatePassword()
        self.assertTrue(self.user.check_password('RaNdOmPaSsWoRd56'))

    def testFormIncorrectCurrentPassword(self):
        testParams = self.TestParams(currentPassword='TEST_PASSWORD', newPassword='RaNdOmPaSsWoRd56',
                                     repeatNewPassword='RaNdOmPaSsWoRd56')
        form = UserSettingsPasswordUpdateForm(request=self.request, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

        for message in form.errors.as_data()['__all__'][0]:
            self.assertEquals(message, 'Your current password does not match with the account\'s existing password.')

    def testFormPasswordMismatch(self):
        testParams = self.TestParams(currentPassword=TEST_PASSWORD, newPassword='RaNdOmPaSsWoRd56',
                                     repeatNewPassword='RaNdOmPaSsWoRd567')
        form = UserSettingsPasswordUpdateForm(request=self.request, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

        for message in form.errors.as_data()['__all__'][0]:
            self.assertEquals(message, 'Your new password and confirm password does not match.')

    def testFormPasswordNotStrong(self):
        testParams = self.TestParams(newPassword='1', repeatNewPassword='1')
        form = UserSettingsPasswordUpdateForm(request=self.request, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

        for message in form.errors.as_data()['__all__'][0]:
            self.assertEquals(message, 'Your new password is not strong enough.')

    # def testFormPasswordReAuthenticate(self):
    #     testParams = self.TestParams(newPassword='RaNdOmPaSsWoRd56', repeatNewPassword='RaNdOmPaSsWoRd56')
    #     form = UserSettingsPasswordUpdateForm(request=self.request, data=testParams.getData())
    #     self.assertTrue(form.is_valid())
    #     form.updatePassword()
    #     self.assertTrue(self.user.check_password('RaNdOmPaSsWoRd56'))
    #     self.assertTrue(form.reAuthenticate(self.client.login))

    class TestParams:

        def __init__(self, currentPassword=TEST_PASSWORD, newPassword=None, repeatNewPassword=None):
            self.currentPassword = currentPassword
            self.newPassword = newPassword
            self.repeatNewPassword = repeatNewPassword

        def getData(self):
            data = {
                'currentPassword': self.currentPassword,
                'newPassword': self.newPassword,
                'repeatNewPassword': self.repeatNewPassword
            }
            return data
