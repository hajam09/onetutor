from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.urls import reverse

from accounts.models import ParentProfile
from accounts.models import StudentProfile
from onetutor.settings import TEST_PASSWORD
from onetutor.tests import userDataHelper
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountCreateStudentProfileViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountCreateStudentProfileViewTest, self).setUp(reverse('accounts:create-student-profile'))
        self.client.login(username=self.user.username, password=TEST_PASSWORD)

    def testAccountCreateStudentProfileGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/createStudentProfile.html')

    def testAccountCreateStudentProfileForAbove18(self):
        testParams = self.TestParams().above18()
        data = testParams.getData()
        response = self.post(data)
        studentProfile = StudentProfile.objects.get(user=self.request.user)

        self.assertEqual(response.status_code, 200)
        self.assertEquals(studentProfile.about, data["about"])
        self.assertEquals(studentProfile.subjects, ', '.join([i.capitalize() for i in data["subjects"]]))
        self.assertIsNone(studentProfile.parent)
        self.assertRedirects(response, '/')
        self.assertEquals(self.request.user.education.count(), 3)

    def testAccountCreateStudentProfileForUnder18(self):
        testParams = self.TestParams().under18()
        data = testParams.getData()
        response = self.post(data)
        studentProfile = StudentProfile.objects.get(user=self.request.user)

        self.assertEqual(response.status_code, 200)
        self.assertEquals(studentProfile.about, data["about"])
        self.assertEquals(studentProfile.subjects, ', '.join([i.capitalize() for i in data["subjects"]]))
        self.assertEquals(studentProfile.parent, testParams.parentProfile.user)  # user
        self.assertRedirects(response, '/')
        self.assertEquals(self.request.user.education.count(), 3)

    def testAccountCreateStudentProfileForUnder18InvalidParentCode(self):
        testParams = self.TestParams().under18()
        testParams.parentIdentifier = "AAAAAAA"
        data = testParams.getData()
        response = self.post(data)
        messages = self.getMessages(response)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/profile/student/create')
        self.assertFalse(StudentProfile.objects.filter(user=self.user).exists())
        self.assertEquals(self.request.user.education.count(), 0)

        for message in messages:
            self.assertEqual(
                str(message),
                'Invalid parent code. We did not find your parent, please check the code again.'
            )

    class TestParams:

        def __init__(self):
            today = datetime.now().date()
            self.dateOfBirth = today
            self.about = "about"
            self.subjects = ["English", "maths", "science"]
            self.parentIdentifier = ""
            self.schoolName = ["School 1", "School 2", "School 3"]
            self.qualification = ["Qualification 1", "Qualification 2", "Qualification 3"]
            self.startDate = [today, today, today]
            self.endDate = [today, today, today]
            self.parentProfile = None

        def above18(self):
            self.dateOfBirth -= relativedelta(years=19)
            return self

        def under18(self):
            self.dateOfBirth -= relativedelta(years=5)
            self.parentProfile = ParentProfile.objects.create(
                user=userDataHelper.createNewUser(),
                dateOfBirth=self.dateOfBirth - relativedelta(years=19)
            )
            self.parentIdentifier = self.parentProfile.code
            return self

        def getData(self):
            data = {
                'about': self.about,
                'subjects': self.subjects,
                'dateOfBirth': self.dateOfBirth,
                'parentIdentifier': self.parentIdentifier,
                'schoolName': self.schoolName,
                'qualification': self.qualification,
                'startDate': self.startDate,
                'endDate': self.endDate,
            }
            return data
