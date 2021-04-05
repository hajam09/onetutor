from django.contrib.auth.models import User
from essential_generators import DocumentGenerator
from accounts.models import TutorProfile
from faker import Faker
import random

EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]

class NewUser:

	def __init__(self):
		self.user = self.createNewUser()
		self.tutorProfile = None
		self.studentProfile = None

	def createNewUser(self):
		fake = Faker()
		first_name = fake.unique.first_name()
		last_name = fake.unique.last_name()
		email = first_name.lower() + '.' + last_name.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)

		user = User.objects.create_user(
			username=email,
			email=email,
			password="RanDomPasWord56",
			first_name=first_name,
			last_name=last_name
		)
		user.save()
		return user

	def createTutorProfile(self):
		gen = DocumentGenerator()
		summary = gen.sentence()
		about = gen.paragraph()

		address_1 = str(randint(1, 100)) + " " + random.choice(STREET_NAME)
		alphabet = list(string.ascii_uppercase)
		postalZip = random.choice(alphabet) + random.choice(alphabet) + str(randint(1, 100)) + " " + str(randint(1, 10)) + random.choice(alphabet) + random.choice(alphabet)

		location = {
			"address_1": address_1,
			"address_2": random.choice(TOWN),
			"city": "London",
			"stateProvince": random.choice(STATE_PROVINCE),
			"postalZip": postalZip,
			"country": {
				"alpha": "GB",
				"name": "United Kingdom"
			}
		}

		school_start_year = randint(1990, 2010)
		school_end_year = school_start_year + randint(3, 5)

		sixth_form_start_year = school_end_year
		sixth_form_end_year = sixth_form_start_year + 2

		uni_start_year = sixth_form_end_year
		uni_end_year = uni_start_year + randint(3, 4)

		education = {
			"education_1": {
				"school_name": random.choice(UNIVERSITIES),
				"qualification": random.choice(DEGREE) + " - " + random.choice(["1st", "2:1", "2:2", "3"]),
				"year": str(uni_start_year) + " - " + str(uni_end_year)
			},
			"education_2": {
				"school_name": random.choice(SCHOOLS),
				"qualification": "A Levels - A*A*AA (Maths, Computing, Further Maths, Physics)",
				"year": str(sixth_form_start_year) + " - " + str(sixth_form_end_year)
			},
			"education_3": {
				"school_name": random.choice(SCHOOLS),
				"qualification": "GCSE - 10 x A* ",
				"year": str(school_start_year) + " - " + str(school_end_year)
			}
		}

		subjects = ', '.join(random.sample(SUBJECTS, 6))

		availability = {
			"monday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"tuesday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"wednesday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"thursday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"friday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"saturday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},
			"sunday": {
				"morning": random.choice(BOOLEAN),
				"afternoon": random.choice(BOOLEAN),
				"evening": random.choice(BOOLEAN)
			},	
		}

		self.tutorProfile = TutorProfile.objects.create(
			user=self.user,
			summary=summary,
			about=about,
			location=location,
			education=education,
			subjects=subjects,
			availability=availability
		)
