import datetime
import decimal
import random
import string

from django.contrib.auth.models import User
from faker import Faker

from accounts.models import TutorProfile, Education, StudentProfile
from onetutor.settings import TEST_PASSWORD
from tutoring.models import Availability, Lesson

EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]

SUBJECTS = {'English', 'Science', 'ICT', 'Religious Studies', 'Maths', 'Games Development', 'Bayesian', 'Statistics',
            'Geography', 'Music', 'History', 'Physics', 'Chemistry', 'Biology'}

UNIVERSITIES = ['Stanford University', 'Harvard University', 'University of Oxford', 'University of Cambridge',
                'Imperial College London',
                'University of Chicago', 'Princeton University', 'Yale University', 'University of Edinburgh',
                'University of Toronto']

DEGREE = ['Accounting and Finance', 'Biology', 'Actuarial Science', 'Aerospace Engineering', 'Business Management',
          'Comparative Literature',
          'Chemical Engineering', 'Chemistry', 'Computer Science', 'Dentistry', 'Drama', 'Economics',
          'Electronic Engineering', 'English',
          'Finance', 'Geography', 'History', 'Law', 'Mathematics', 'Mechanical Engineering', 'Physics', 'Neuroscience']

SCHOOLS = ['Dame Elizabeth Cadbury School', 'Brooke House College', 'Hope Academy', 'Scarisbrick Hall School',
           'Exeter Tutorial College',
           'Valley Park School', 'Bredon School', 'Hurtwood House School']

TOWN = ['Barking', 'Eastham', 'Upton Park', 'Plaistow', 'Westham', 'Mile End', 'Stratford', 'Dagenham', 'Hammersmith',
        'Islington', 'Templte', 'Westminister', 'Embankment', 'Barbican', 'Blackfriars', 'Angel', 'Marylebone',
        'Knightsbridge', 'Monument', 'Bank', 'Holborn', 'Waterloo', 'Limehouse', 'Highgate', 'Stanmore', 'Aldgate']

STATE_PROVINCE = ['Cardiff', 'Cumbria', 'Durham', 'East Sussex', 'Essex', 'Hartlepool', 'Kent',
                  'Northumberland', 'Somerset', 'Suffolk', 'Swansea', 'West Sussex', 'York']

STREET_NAME = ['High Street', 'Station Road', 'Main Street', 'Park Road', 'Church Road',
               'Church Street', 'London Road', 'Victoria Road', 'Green Lane', 'Manor Road',
               'Church Lane', 'Park Avenue', 'The Avenue', 'The Crescent', 'Queens Road',
               'New Road', 'Grange Road', 'Kings Road', 'Kingsway', 'Windsor Road',
               'Highfield Road', 'Mill Lane', 'Alexander Road', 'York Road', 'Main Road',
               'Broadway', 'King Street', 'Springfield Road', 'George Street', 'Park Lane',
               'Victoria Street', 'Albert Road', 'Queensway', 'New Street', 'Queen Street',
               'West Street', 'North Street', 'Manchester Road', 'The Grove', 'Richmond Road',
               'Grove Road', 'South Street', 'School Lane', 'The Drive', 'North Road', 'Stanley Road',
               'Chester Road', 'Mill Road']


def createNewUser():
    faker = Faker()

    firstName = faker.unique.first_name()
    lastName = faker.unique.last_name()
    email = firstName.lower() + '.' + lastName.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=TEST_PASSWORD,
        first_name=firstName,
        last_name=lastName
    )
    user.save()
    return user


def createTutorProfileForUser(user=None):
    if user is None:
        user = createNewUser()

    summary = "gen.sentence()"
    about = "gen.paragraph()"
    subjects = ', '.join(random.sample(SUBJECTS, 6))

    schoolStartYear = random.randint(1990, 2010)
    schoolEndYear = schoolStartYear + random.randint(3, 5)
    sixthFormStartYear = schoolEndYear
    sixthFormEndYear = sixthFormStartYear + + random.randint(2, 4)
    uniStartYear = sixthFormEndYear
    uniEndYear = uniStartYear + random.randint(3, 4)

    Education.objects.bulk_create(
        [
            # E1 - university
            Education(
                user=user,
                schoolName=random.choice(UNIVERSITIES),
                qualification=random.choice(DEGREE) + " - " + random.choice(["1st", "2:1", "2:2", "3"]),
                startDate=datetime.datetime(uniStartYear, 9, 1),
                endDate=datetime.datetime(uniEndYear, 6, 10),
            ),
            # E2 - sixth-form
            Education(
                user=user,
                schoolName=random.choice(SCHOOLS),
                qualification="{} - {}".format("A Levels", ', '.join(random.sample(SUBJECTS, random.randint(3, 5)))),
                startDate=datetime.datetime(sixthFormStartYear, 9, 1),
                endDate=datetime.datetime(sixthFormEndYear, 7, 14),
            ),
            # E3 - secondary school
            Education(
                user=user,
                schoolName=random.choice(SCHOOLS),
                qualification="{} - {}".format("GCSE", ', '.join(random.sample(SUBJECTS, random.randint(5, 8)))),
                startDate=datetime.datetime(schoolStartYear, 9, 1),
                endDate=datetime.datetime(schoolEndYear, 7, 14),
            )
        ]
    )

    address_1 = str(random.randint(1, 100)) + " " + random.choice(STREET_NAME)
    alphabet = list(string.ascii_uppercase)
    postalZip = random.choice(alphabet) + random.choice(alphabet) + str(random.randint(1, 100)) + " " + str(
        random.randint(1, 10)) + random.choice(alphabet) + random.choice(alphabet)

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

    newTutorProfile = TutorProfile.objects.create(
        user=user,
        summary=summary,
        about=about,
        location=location,
        subjects=subjects,
        chargeRate=random.randint(10, 100),
    )

    allFeatures = Feature.objects.all()
    newTutorProfile.features.add(*random.sample(list(allFeatures), random.randint(0, allFeatures.count())))

    Availability.objects.create(
        user=user
    )
    return newTutorProfile


def createNewUserAndStudentProfile(user=None):
    if user is None:
        user = createNewUser()

    about = "gen.paragraph()"
    subjects = ', '.join(random.sample(SUBJECTS, 6))
    alsoSixthForm = random.choice(BOOLEAN)

    schoolStartYear = random.randint(1990, 2010)
    schoolEndYear = schoolStartYear + random.randint(3, 5)
    sixthFormStartYear = schoolEndYear
    sixthFormEndYear = sixthFormStartYear + + random.randint(2, 4)

    if alsoSixthForm:
        # E2 - sixth-form
        Education.objects.create(
            user=user,
            schoolName=random.choice(SCHOOLS),
            qualification="{} - {}".format("A Levels", ', '.join(random.sample(SUBJECTS, random.randint(3, 5)))),
            startDate=datetime.datetime(sixthFormStartYear, 9, 1),
            endDate=datetime.datetime(sixthFormEndYear, 7, 14),
        )

    # E3 - secondary school
    Education.objects.create(
        user=user,
        schoolName=random.choice(SCHOOLS),
        qualification="{} - {}".format("GCSE", ', '.join(random.sample(SUBJECTS, random.randint(5, 8)))),
        startDate=datetime.datetime(schoolStartYear, 9, 1),
        endDate=datetime.datetime(schoolEndYear, 7, 14),
    )

    newStudentProfile = StudentProfile.objects.create(
        user=user,
        about=about,
        subjects=subjects
    )
    return newStudentProfile


def createLessonsForTutor(tutor, numberOfLessons):
    Lesson.objects.bulk_create(
        [
            Lesson(
                tutor=tutor,
                hoursTaught=decimal.Decimal(random.randrange(155, 389)) / 100,
                points=random.randint(0, 10),
                amount=decimal.Decimal(random.randrange(155, 389)) / 100 * tutor.chargeRate
            )
            for _ in range(numberOfLessons)
        ]
    )
    return


def createLessonsAllTutors():
    allTutors = TutorProfile.objects.all()

    for tutor in allTutors:
        Lesson.objects.bulk_create(
            [
                Lesson(
                    tutor=tutor,
                    hoursTaught=decimal.Decimal(random.randrange(155, 389)) / 100,
                    points=random.randint(0, 10),
                    amount=decimal.Decimal(random.randrange(155, 389)) / 100 * tutor.chargeRate
                )
                for _ in range(random.randint(2, 6))
            ]
        )
    return
