import datetime

from django.urls import reverse

from accounts.models import TutorProfile
from dashboard.models import UserLogin
from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews
from tutoring.models import Availability


class AccountCreateTutorProfileTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountCreateTutorProfileTest, self).setUp(reverse('accounts:create-tutor-profile'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)
        self.userLogin = UserLogin.objects.create(user=self.request.user)

    def testCreateTutorProfileGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/createTutorProfile.html')

    def testCreateTutorProfile(self):
        testParams = self.TestParams()
        data = testParams.getData()
        response = self.post(data)
        tutorProfile = TutorProfile.objects.get(user=self.request.user)

        self.assertEquals(tutorProfile.summary, data["summary"])
        self.assertEquals(tutorProfile.about, data["about"])
        self.assertEquals(tutorProfile.subjects, ', '.join([i.capitalize() for i in data["subjects"]]))
        self.assertEquals(self.request.user.education.count(), 3)
        self.assertTrue(Availability.objects.filter(user=self.user).exists())
        self.assertEquals(response.status_code, 200)
        self.assertRedirects(response, '/')

    class TestParams:

        def getData(self):
            today = datetime.date.today()
            data = {
                "createTutorProfile": "",
                "summary": "summary",
                "about": "about",
                "subjects": ["English", "Maths"],
                "chargeRate": "10",
                "schoolName": ["School 1", "School 2", "School 3"],
                "qualification": ["Qualification 1", "Qualification 2", "Qualification 3"],
                "startDate": [today, today, today],
                "endDate": [today, today, today],
            }
            return data
