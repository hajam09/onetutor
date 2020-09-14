from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.urls import reverse

from accounts.models import ParentProfile
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountCreateParentProfileViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountCreateParentProfileViewTest, self).setUp(reverse('accounts:create-parent-profile'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testAccountCreateParentProfileGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/createParentProfile.html')

    def testAccountCreateParentProfileForAbove18(self):
        testParams = self.TestParams().above18()
        response = self.post(testParams.getData())

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/user-settings/parent/general')
        self.assertIsNotNone(self.user.parentProfile)

    def testAccountCreateParentProfileForUnder18(self):
        testParams = self.TestParams().under18()
        response = self.post(testParams.getData())
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/profile/parent/create')
        self.assertFalse(ParentProfile.objects.filter(user=self.user).exists())

        for message in messages:
            self.assertEqual(
                str(message),
                'You need to be at least 18 years to create an account.'
            )

    class TestParams:

        def __init__(self):
            self.dateOfBirth = datetime.now().date()

        def above18(self):
            self.dateOfBirth -= relativedelta(years=19)
            return self

        def under18(self):
            self.dateOfBirth -= relativedelta(years=5)
            return self

        def getData(self):
            data = {
                'dateOfBirth': self.dateOfBirth,
            }
            return data
