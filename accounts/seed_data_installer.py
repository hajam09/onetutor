from django.template.defaultfilters import slugify

from accounts.models import Countries
from accounts.models import Subject
from accounts.models import TutorProfile
from deprecated import deprecated
from django.contrib.auth.models import User
from django.db import connection
from forum.models import Category
from forum.models import Community
from forum.models import Forum
from forum.models import ForumComment
from pathlib import Path
from random import randint
import json
import random
import string
# 
from essential_generators import DocumentGenerator
from faker import Faker
import names

CRON = []
all_tables = connection.introspection.table_names()

# CONSTANT VALUES
EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]

STREET_NAME = ['High Street' , 'Station Road' , 'Main Street' , 'Park Road' , 'Church Road' ,
				'Church Street' , 'London Road' , 'Victoria Road' , 'Green Lane' , 'Manor Road' ,
				'Church Lane' , 'Park Avenue' , 'The Avenue' , 'The Crescent' , 'Queens Road' ,
				'New Road' , 'Grange Road' , 'Kings Road' , 'Kingsway' , 'Windsor Road' ,
				'Highfield Road' , 'Mill Lane' , 'Alexander Road' , 'York Road' , 'Main Road' ,
				'Broadway' , 'King Street' , 'Springfield Road' , 'George Street' , 'Park Lane' ,
				'Victoria Street' , 'Albert Road' , 'Queensway' , 'New Street' , 'Queen Street' ,
				'West Street' , 'North Street' , 'Manchester Road' , 'The Grove' , 'Richmond Road' ,
				'Grove Road' , 'South Street' , 'School Lane' , 'The Drive' , 'North Road' , 'Stanley Road' ,
				'Chester Road' , 'Mill Road']

TOWN = ['Barking', 'Eastham', 'Upton Park', 'Plaistow', 'Westham', 'Mile End', 'Stratford', 'Dagenham', 'Hammersmith',
		'Islington', 'Templte', 'Westminister', 'Embankment', 'Barbican', 'Blackfriars', 'Angel', 'Marylebone',
		'Knightsbridge', 'Monument', 'Bank', 'Holborn', 'Waterloo', 'Limehouse', 'Highgate', 'Stanmore', 'Aldgate']

STATE_PROVINCE = ['Cardiff', 'Cumbria', 'Durham', 'East Sussex', 'Essex', 'Hartlepool', 'Kent',
				'Northumberland', 'Somerset', 'Suffolk', 'Swansea', 'West Sussex', 'York']
SUBJECTS = set(['English', 'Science', 'ICT', 'Religious Studies', 'Maths', 'Games Development', 'Bayesian',
			'Statistics', 'Geography', 'Music', 'History', 'Physics', 'Chemistry', 'Biology'])


UNIVERSITIES = ['Stanford University', 'Harvard University', 'University of Oxford', 'University of Cambridge', 'Imperial College London',
				'University of Chicago', 'Princeton University', 'Yale University', 'University of Edinburgh', 'University of Toronto']

DEGREE = ['Accounting and Finance', 'Biology', 'Actuarial Science', 'Aerospace Engineering', 'Business Management', 'Comparative Literature',
			'Chemical Engineering', 'Chemistry', 'Computer Science', 'Dentistry', 'Drama', 'Economics', 'Electronic Engineering', 'English',
			'Finance', 'Geography', 'History', 'Law', 'Mathematics', 'Mechanical Engineering', 'Physics', 'Neuroscience']

SCHOOLS = ['Dame Elizabeth Cadbury School', 'Brooke House College', 'Hope Academy', 'Scarisbrick Hall School', 'Exeter Tutorial College',
			'Valley Park School', 'Bredon School', 'Hurtwood House School']

def install_TutorProfile():
	if 'accounts_tutorprofile' not in all_tables:
		return

	if TutorProfile.objects.all().count() >= 20:
		return

	for __ in range(2):
		fake = Faker()
		gen = DocumentGenerator()

		first_name = fake.unique.first_name()
		last_name = fake.unique.last_name()
		email = first_name.lower() + '.' + last_name.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)
		password = 'RanDomPasWord56'

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
		  }
		}

		user = User.objects.create( username=email, email=email, password=password, first_name=first_name, last_name=last_name )
		TutorProfile.objects.create(user=user,summary=gen.sentence(),about=gen.paragraph(),location=location,education=education,subjects=subjects,availability=availability)
	return

@deprecated(reason="No longer creates reliable data.")
def emailaddress(firstname, lastname):
	firstname = firstname.lower()
	lastname = lastname.lower()
	return firstname+"."+lastname+"@gmail.com"

@deprecated(reason="No longer creates reliable data.")
def installTutorFromFaker():
	for i in range(2):
		gen = DocumentGenerator()
		fake = Faker()
		# account: username, email, password, first_name, last_name
		first_name = names.get_first_name()
		last_name = names.get_last_name()
		email = emailaddress(first_name, last_name)
		username = emailaddress(first_name, last_name)
		password = 'RanDomPasWord56'
		# TutorProfile: user, summary, about, location, education, subjects, availability, profilePicture
		summary = gen.sentence()
		about = gen.paragraph()
		location = { "address_1": "24 London Road", "address_2": "Barking", "city": "London", "stateProvince": "Essex", "postalZip": "QR11 2TV", "country": { "alpha": "GB", "name": "United Kingdom" } }
		education = { "education_1": { "school_name": "Imperial College London", "qualification": "Computing (Masters) - 2:1 (2016 - 2020)", "year": "Peter Symonds College" }, "education_2": { "school_name": "Peter Symonds College", "qualification": "A Levels - A*A*AA (Maths, Computing, Further Maths, Physics)", "year": "2014 - 2016" }, "education_3": { "school_name": "Perins School", "qualification": "GCSE - 10 x A* ", "year": "2009 - 2014" } }
		subjects = "English, Maths, Science, ICT, RE, Statistics, DT, Computing, Games Development, Networks, Web Programming, GUI, Bayesian"
		availability = None
		profilePicture = None

		user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
		TutorProfile.objects.create(user=user, summary=summary, about=about, location=location, education=education, subjects=subjects, availability=None)
	return

def installCountries():
	if installCountries in CRON:
		CRON.remove(installCountries)

	if 'accounts_countries' not in all_tables:
		CRON.append(installCountries)
		return

	for i in open("seed-data/countries.txt", "r").readlines():
		i = i.replace("\n", "").split("|")
		if not Countries.objects.filter(alpha=i[0]).exists():
			Countries.objects.create(alpha=i[0], name=i[1])

	print("Countries table created and populated")
	return

def installTutor():
	if installTutor in CRON:
		CRON.remove(installTutor)

	if 'accounts_tutorprofile' not in all_tables:
		CRON.append(installTutor)
		return

	pathToFile = str(Path(__file__).resolve().parent.parent) + '\\seed-data\\tutors.json'
	with open(pathToFile) as f:
		data = json.load(f)
		for d in data:
			if not User.objects.filter(email=d["email"]).exists():
				user = User.objects.create_user(username=d["username"], email=d["email"], password=d["password"], first_name=d["first_name"], last_name=d["last_name"])
				TutorProfile.objects.create(user=user, summary=d["summary"], about=d["about"],
											location=d["location"], education=d["education"], subjects=d["subjects"], availability=d["availability"])
	return

def installSubjects():
	if installSubjects in CRON:
		CRON.remove(installSubjects)

	if 'accounts_subject' not in all_tables:
		CRON.append(installSubjects)
		return

	for i in open("seed-data/subjects.txt", "r").readlines():
		i = i.replace("\n", "")
		if not Subject.objects.filter(name=i).exists():
			Subject.objects.create(name=i)
	print("Subject table created and populated")
	return

def installCategories():
	if installCategories in CRON:
		CRON.remove(installCategories)

	if 'forum_category' not in all_tables:
		CRON.append(installCategories)
		return

	for i in open("seed-data/categories.txt", "r").readlines():
		i = i.replace("\n", "")
		if not Category.objects.filter(name=i).exists():
			Category.objects.create(name=i)
	print("Category table created and populated")
	return

def installCommunity(totalValue):
	if installCommunity in CRON:
		CRON.remove(installCommunity)

	if 'forum_community' not in all_tables:
		CRON.append(installCommunity)
		return

	categoryCount = Category.objects.count()
	if categoryCount == 0 or categoryCount >= 10:
		return

	community_bulk_object = []
	for i in range(totalValue):
		gen = DocumentGenerator()
		creator = random.choice(User.objects.all().exclude(is_superuser=True))
		title = gen.sentence()
		url = slugify(title)
		tags = ", ".join([gen.word() for _ in range(5)])
		description = gen.paragraph()

		community_bulk_object.append(
			Community(
				creator=creator,
				title=title,
				url=url,
				tags=tags,
				description=description,
			)
		)

	Community.objects.bulk_create(community_bulk_object)
	print("Community table created and populated")
	return


def installForum(totalValue):
	if installForum in CRON:
		CRON.remove(installForum)

	if 'forum_forum' not in all_tables:
		CRON.append(installForum)
		return

	if Community.objects.count() == 0:
		return#installCommunity(10)

	if Forum.objects.count() >= 99:
		return

	forum_bulk_object = []
	for i in range(totalValue):
		gen = DocumentGenerator()
		community = random.choice(Community.objects.all())
		creator = random.choice(User.objects.all().exclude(is_superuser=True))
		title = gen.sentence()
		url = slugify(title)
		description = gen.paragraph()
		anonymous = random.choice([True, False])

		forum_bulk_object.append(
			Forum(
				community=community,
				creator=creator,
				title=title,
				url=url,
				description=description,
				anonymous=anonymous
			)
		)

	Forum.objects.bulk_create(forum_bulk_object)
	print("Forum table created and populated")
	return

def installForumComment(totalValue):
	if installForumComment in CRON:
		CRON.remove(installForumComment)

	if 'forum_forumcomment' not in all_tables:
		CRON.append(installForumComment)
		return

	if Forum.objects.count() == 0:
		return

	if ForumComment.objects.count() >= 99:
		return

	forumComment_bulk_object = []
	for i in range(totalValue):
		if ForumComment.objects.count() >=100:
			return
		gen = DocumentGenerator()
		forum = random.choice(Forum.objects.all())
		creator = random.choice(User.objects.all().exclude(is_superuser=True))
		comment_description = gen.paragraph()

		forumComment_bulk_object.append(
			ForumComment(
				forum = forum,
				creator = creator,
				comment_description = comment_description,
			)
		)

	ForumComment.objects.bulk_create(forumComment_bulk_object)
	print("ForumComment table created and populated")
	return