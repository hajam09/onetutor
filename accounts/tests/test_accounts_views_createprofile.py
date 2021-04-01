from accounts.models import TutorProfile
from accounts.seed_data_installer import installCountries
from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from unittest import skip

# coverage run --source=accounts manage.py test accounts
# coverage html

@skip("Running multiple tests simultaneously slows down the process")
class TestAccountViewsCreateTutorProfile(TestCase):
	"""
		Testing the create profile view where the user can create tutor profile.
	"""

	def setUp(self):
		self.client = Client(HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
		self.url = reverse('accounts:createprofile')
		self.user_1 = User.objects.create_user(username=AccountValueSet.USER_1_USERNAME,
			email=AccountValueSet.USER_1_USERNAME,
			password=AccountValueSet.USER_STRONG_PASSWORD,
			first_name="Barry",
			last_name="Allen"
		)
		self.client.login(username=AccountValueSet.USER_1_USERNAME, password=AccountValueSet.USER_STRONG_PASSWORD)
		installCountries()

	def test_createprofile_GET(self):
		"""
			User must be authenticated prior to calling the view.
		"""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'accounts/createprofile.html')

	# @skip("Don't want to test")
	def test_createprofile_create_tutor_profile(self):
		"""
			User must be authenticated prior to calling the view.
			Creating a tutor profile for this user.
		"""
		context = {
			"tutor": "",
			"summary": "Summary for this particular tutor.",
			"about": "Short about section for this tutor.",
			"subjects": "English, Maths, Science, ICT",
			"numberOfEducation": "1" ,
			"school_name_1": "ECS",
			"qualification_1": "A-Levels",
			"year_1": "2010-2015",
			"country": "GB",
			"address_1": "99 Some Road",
			"address_2": "becontree",
			"city": "Cambridge",
			"stateProvince": "Sussex",
			"postalZip": "MU8 3SW",
		}
		count_before = TutorProfile.objects.all().count()
		response = self.client.post(self.url, context)
		self.assertEquals(response.status_code, 302)
		self.assertEqual(TutorProfile.objects.all().count(), count_before + 1)
		self.assertEqual(TutorProfile.objects.all().order_by('-id')[0].user, self.user_1)

	# @skip("Don't want to test")
	def test_createprofile_tutor_profile_exists(self):
		"""
			User must be authenticated prior to calling the view.
			If user 1 is logged in and creates tutor profile, then redirect to tutorprofile view.
		"""
		self.test_createprofile_create_tutor_profile()
		response = self.client.post(self.url, {})
		self.assertEquals(response.status_code, 302)

@skip("Don't want to test")
class TestAccountViewsCreateStudentProfile(TestCase):
	pass