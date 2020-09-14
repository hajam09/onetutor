from accounts.forms import PasswordChangeForm
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTest import BaseTest


class PasswordChangeFormTest(BaseTest):

    def setUp(self) -> None:
        super(PasswordChangeFormTest, self).setUp('')
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testFormIsValid(self):
        testParams = self.TestParams(password='RaNdOmPaSsWoRd56', repeatPassword='RaNdOmPaSsWoRd56')
        form = PasswordChangeForm(request=self.request, user=self.user, data=testParams.getData())
        self.assertTrue(form.is_valid())
        form.updatePassword()
        self.assertTrue(self.user.check_password('RaNdOmPaSsWoRd56'))

    def testFormPasswordMismatch(self):
        testParams = self.TestParams(password='RaNdOmPaSsWoRd56', repeatPassword='RaNdOmPaSsWoRd567')
        form = PasswordChangeForm(request=self.request, user=self.user, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

        for message in form.errors.as_data()['__all__'][0]:
            self.assertEquals(message, 'Your new password and confirm password does not match.')

    def testFormPasswordNotStrong(self):
        testParams = self.TestParams(password='1', repeatPassword='1')
        form = PasswordChangeForm(request=self.request, user=self.user, data=testParams.getData())
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

        for message in form.errors.as_data()['__all__'][0]:
            self.assertEquals(message, 'Your new password is not strong enough.')

    class TestParams:

        def __init__(self, password, repeatPassword):
            self.password = password
            self.repeatPassword = repeatPassword

        def getData(self):
            data = {
                'password': self.password,
                'repeatPassword': self.repeatPassword
            }
            return data
