from .models import Countries, Subject, TutorProfile
import json
from pathlib import Path
from django.contrib.auth.models import User
from forum.models import Community, Forum

# 
import names
from essential_generators import DocumentGenerator
from faker import Faker

def emailaddress(firstname, lastname):
	firstname = firstname.lower()
	lastname = lastname.lower()
	return firstname+"."+lastname+"@gmail.com"

def passwordGenerate():
	return "Maideen69"

def usertype(arg):
	if(arg=="tutor"):
		return "TUTOR"
	return "STUDENT"

def installTutorFromFaker():
	for i in range(2):
		gen = DocumentGenerator()
		fake = Faker()
		# account: username, email, password, first_name, last_name
		first_name = names.get_first_name()
		last_name = names.get_last_name()
		email = emailaddress(first_name, last_name)
		username = emailaddress(first_name, last_name)
		password = passwordGenerate()
		# TutorProfile: user, userType, summary, about, location, education, subjects, availability, profilePicture
		userType = "TUTOR"
		summary = gen.sentence()
		about = gen.paragraph()
		location = { "address_1": "24 Cranborne Road", "address_2": "Barking", "city": "London", "stateProvice": "Essex", "postalZip": "IG11 7XE", "country": { "alpha": "GB", "name": "United Kingdom" } }
		education = { "education_1": { "school_name": "Imperial College London", "qualification": "Computing (Masters) - 2:1 (2016 - 2020)", "year": "Peter Symonds College" }, "education_2": { "school_name": "Peter Symonds College", "qualification": "A Levels - A*A*AA (Maths, Computing, Further Maths, Physics)", "year": "2014 - 2016" }, "education_3": { "school_name": "Perins School", "qualification": "GCSE - 10 x A* ", "year": "2009 - 2014" } }
		subjects = "English, Maths, Science, ICT, RE, Statistics, DT, Computing, Games Development, Networks, Web Programming, GUI, Bayesian"
		availability = None
		profilePicture = None

		user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
		TutorProfile.objects.create(user=user, userType="TUTOR", summary=summary, about=about, location=location, education=education, subjects=subjects, availability=None, profilePicture=None)
	return
# 

def installCountries():
	# Countries.objects.all().delete()
	for i in open("seed-data/countries.txt", "r").readlines():
		i = i.replace("\n", "").split("|")
		if not Countries.objects.filter(alpha=i[0]).exists():
			Countries.objects.create(alpha=i[0], name=i[1])
	return

def installTutor():
	pathToFile = str(Path(__file__).resolve().parent.parent) + '\\seed-data\\tutors.json'
	with open(pathToFile) as f:
		data = json.load(f)
		for d in data:
			if not User.objects.filter(email=d["email"]).exists():
				user = User.objects.create_user(username=d["username"], email=d["email"], password=d["password"], first_name=d["first_name"], last_name=d["last_name"])
				TutorProfile.objects.create(user=user, userType=d["userType"], summary=d["summary"], about=d["about"],
											location=d["location"], education=d["education"], subjects=d["subjects"], availability=d["availability"], profilePicture=None)
	return

def installSubjects():
	for i in open("seed-data/subjects.txt", "r").readlines():
		i = i.replace("\n", "")
		if not Subject.objects.filter(name=i).exists():
			Subject.objects.create(name=i)
	return

def installForum():
	for i in range(100):
		gen = DocumentGenerator()
		random_community = random.choice(Community.objects.all())
		random_creator = random.choice(User.objects.all())
		random_forum_title = gen.sentence()
		random_forum_url = ''.join(e for e in random_forum_title if e.isalnum())
		random_forum_description = gen.paragraph()
		random_anonymous = False

		Forum.objects.create(
			community=random_community,
			creator=creator,
			forum_title=random_forum_title,
			forum_url=random_forum_url,
			forum_description=random_forum_description,
			anonymous=anonymous
		)
	return

def main():
	installCountries()
	installTutor()
	installSubjects()
	# installTutorFromFaker()
	# installForum()
	return

main()