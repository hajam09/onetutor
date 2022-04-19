from datetime import datetime
from unittest.mock import patch

from django.urls import reverse
from faker import Faker
from unittest import skip

from accounts.models import GetInTouch
from onetutor.tests.BaseTestViews import BaseTestViews


class AccountGetInTouchViewTest(BaseTestViews):

    def setUp(self) -> None:
        super(AccountGetInTouchViewTest, self).setUp(reverse('accounts:get-in-touch'))

    def testGetInTouchGet(self):
        response = self.get()
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'footer/getInTouch.html')

    @skip('Test passes in debug mode only')
    @patch('accounts.views.GetInTouchForm.is_valid')
    def testRegisterAccountSuccess(self, mockGetInTouchForm):
        mockGetInTouchForm.return_value = True
        testParams = self.TestParams()
        data = testParams.getData()
        response = self.post(data)
        messages = list(response.context['messages'])

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/get-in-touch/')
        self.assertEqual(len(messages), 1)

        getInTouch = GetInTouch.objects.filter(fullName=data['fullName'], email=data['email']).last()
        self.assertEqual(getInTouch.dateTime.date(), datetime.now().date())

        for message in messages:
            self.assertEqual(
                str(message),
                'Your message has been received, We will contact you soon.'
            )

    @patch('accounts.views.GetInTouchForm.is_valid')
    def testGetInTouchFailed(self, mockGetInTouchForm):
        mockGetInTouchForm.return_value = False
        testParams = self.TestParams()
        response = self.post(testParams.getData())
        self.assertNotEqual(response.context['form'], None)

    class TestParams:

        def getData(self):
            faker = Faker()
            data = {
                'fullName': faker.unique.first_name() + " " + faker.unique.last_name(),
                'email': faker.safe_email(),
                'subject': faker.sentence(nb_words=10),
                'message': faker.paragraph(nb_sentences=5)
            }
            return data
