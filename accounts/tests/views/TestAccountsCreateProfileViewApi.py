from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse

from onetutor.settings import TEST_PASSWORD
from onetutor.tests.BaseTestViews import BaseTestViews

class TestAccountsCreateProfileViewApi(BaseTestViews):

    def setUp(self) -> None:
        super(TestAccountsCreateProfileViewApi, self).setUp(reverse("accounts:create-profile"))


    def testGetProfileTemplateWhenNoQueryIsPassed(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/selectProfileTemplate.html")

    def testGetTutorTemplateWhenTutorQueryIsPassed(self):
        self.path = reverse("accounts:create-profile") + "?type=tutor"
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/createTutorProfile.html")

    def testGetStudentTemplateWhenTutorQueryIsPassed(self):
        self.path = reverse("accounts:create-profile") + "?type=student"
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/createStudentProfile.html")

    def testGetParentTemplateWhenTutorQueryIsPassed(self):
        self.path = reverse("accounts:create-profile") + "?type=parent"
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/createParentProfile.html")

    def testExceptionWhenTypeQueryIsNotRecognised(self):
        with self.assertRaises(NotImplementedError):
            self.path = reverse("accounts:create-profile") + "?type=random"
            response = self.get()
            self.assertEquals(response.status_code, 200)


    def testHandleStudentProfileParentNotFoundOrCodeInvalid(self):
        pass


    class StudentTestParams:

        def __init__(self, email, password):
            self.email = email
            self.password = password

        def getData(self):
            data = {
                'email': self.email,
                'password': self.password,
            }
            return data

