import decimal
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from faker import Faker

from accounts.models import ComponentGroup, Component, TutorProfile, Subject, StudentProfile, ParentProfile, Education
from onetutor.operations import seedDataOperations
from tutoring.models import Availability, TutorReview, Lesson


class Command(BaseCommand):
    PASSWORD = 'admin'
    TUTOR_PROFILE_COUNT = 200
    STUDENT_PROFILE_COUNT = 160 // 2

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')
        self.subjects = None
        self.tutorFeatures = None
        self.teachingLevels = None
        self.QUALIFICATIONS = [
            "Higher Secondary", "Foundation Degree", "Bachelor Degree", "Master Degree", "Doctorate Degree"
        ]

    def handle(self, *args, **kwargs):
        try:
            adminUser = User(
                username='admin',
                email='django.admin@example.com',
                first_name='Django',
                last_name='Admin',
                is_staff=True,
                is_active=True,
                is_superuser=True,
            )
            adminUser.set_password(Command.PASSWORD)
            adminUser.save()
        except IntegrityError:
            pass

        User.objects.filter(is_staff=False).delete()
        ComponentGroup.objects.all().delete()
        Component.objects.all().delete()
        Subject.objects.all().delete()
        TutorProfile.objects.all().delete()
        StudentProfile.objects.all().delete()
        ParentProfile.objects.all().delete()
        Education.objects.all().delete()
        Availability.objects.all().delete()
        TutorReview.objects.all().delete()
        Lesson.objects.all().delete()

        print("Attempting to run seed data installer")
        seedDataOperations.runSeedDataInstaller()

        self.subjects = Subject.objects.all()
        self.tutorFeatures = Component.objects.filter(componentGroup__code="TUTOR_FEATURE")
        self.teachingLevels = Component.objects.filter(componentGroup__code="EDUCATION_LEVEL")
        print("Attempting to seed data")

        try:
            with transaction.atomic():
                print(f'Attempting to create {Command.TUTOR_PROFILE_COUNT} tutor users.')
                self.bulkCreateTutorProfiles()

                print(f'Attempting to create {Command.STUDENT_PROFILE_COUNT} student and parent users.')
                self.bulkCreateStudentProfiles()

                print(f'Attempting to create tutor reviews.')
                self.bulkCreateTutorReviews()

                print(f'Attempting to create lessons.')
                self.bulkCreateLessons()

                print('Item seeding complete.')
        except BaseException:
            print('Failed to seed data. Rolled back all the transactions')

    def _email(self, first_name, last_name):
        return f'{first_name}.{last_name}@{self.faker.free_email_domain()}'

    def createUser(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = self._email(first_name.lower(), last_name.lower())

        user = User()
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = email
        user.set_password(Command.PASSWORD)
        return user

    def bulkCreateTutorProfiles(self):
        USERS = []
        TUTOR_PROFILES = []
        EDUCATION_LIST = []
        AVAILABILITY_LIST = []
        for i in range(Command.TUTOR_PROFILE_COUNT):
            user = self.createUser()

            tutorProfile = TutorProfile(
                user=user,
                summary=self.faker.pystr_format(),
                about=self.faker.paragraph(),
                subjects="&#44;".join([subject.name for subject in random.sample(list(self.subjects), 5)]),
                chargeRate=float(decimal.Decimal(random.randrange(0, 1000)) / 100)
            )
            USERS.append(user)
            TUTOR_PROFILES.append(tutorProfile)

            for j in range(random.randint(1, 4)):
                education = Education(
                    user=user,
                    schoolName=self.faker.pystr_format(),
                    qualification=random.choice(self.QUALIFICATIONS),
                    startDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                    endDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                )
                EDUCATION_LIST.append(education)

            AVAILABILITY_LIST.append(
                Availability(user=user)
            )

        User.objects.bulk_create(USERS)
        TutorProfile.objects.bulk_create(TUTOR_PROFILES)
        Education.objects.bulk_create(EDUCATION_LIST)
        Availability.objects.bulk_create(AVAILABILITY_LIST)

        tutorProfiles = TutorProfile.objects.all()
        for profile in tutorProfiles:
            profile.features.add(
                *[i.id for i in random.sample(list(self.tutorFeatures), 3)]
            )
            profile.teachingLevels.add(
                *[i.id for i in random.sample(list(self.teachingLevels), 4)]
            )
        return

    def bulkCreateStudentProfiles(self):
        USERS = []
        PARENT_PROFILE = []
        STUDENT_PROFILE = []
        EDUCATION_LIST = []

        for i in range(Command.STUDENT_PROFILE_COUNT):
            parentUser = self.createUser()
            studentAUser = self.createUser()
            studentBUser = self.createUser()

            parentProfile = ParentProfile(
                user=parentUser,
                dateOfBirth=datetime.now() - relativedelta(years=random.randint(18, 50))
            )

            studentA = StudentProfile(
                user=studentAUser,
                about=self.faker.paragraph(),
                subjects="&#44;".join([subject.name for subject in random.sample(list(self.subjects), 5)]),
                dateOfBirth=datetime.now() - relativedelta(years=random.randint(11, 18)),
                parent=parentUser
            )

            studentB = StudentProfile(
                user=studentBUser,
                about=self.faker.paragraph(),
                subjects="&#44;".join([subject.name for subject in random.sample(list(self.subjects), 5)]),
                dateOfBirth=datetime.now() - relativedelta(years=random.randint(11, 18)),
                parent=parentUser
            )

            for j in range(random.randint(1, 2)):
                educationA = Education(
                    user=studentAUser,
                    schoolName=self.faker.pystr_format(),
                    qualification=random.choice(self.QUALIFICATIONS),
                    startDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                    endDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                )
                educationB = Education(
                    user=studentBUser,
                    schoolName=self.faker.pystr_format(),
                    qualification=random.choice(self.QUALIFICATIONS),
                    startDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                    endDate=datetime.now() - relativedelta(years=random.randint(11, 18)),
                )
                EDUCATION_LIST.extend([educationA, educationB])

            USERS.extend([parentUser, studentAUser, studentBUser])
            PARENT_PROFILE.append(parentProfile)
            STUDENT_PROFILE.extend([studentA, studentB])

        User.objects.bulk_create(USERS)
        ParentProfile.objects.bulk_create(PARENT_PROFILE)
        StudentProfile.objects.bulk_create(STUDENT_PROFILE)
        Education.objects.bulk_create(EDUCATION_LIST)
        return

    def bulkCreateTutorReviews(self):
        tutorProfiles = TutorProfile.objects.all()
        studentProfiles = StudentProfile.objects.all()

        for tutor in tutorProfiles:
            TUTOR_REVIEWS = []
            for i in range(70):
                TUTOR_REVIEWS.append(
                    TutorReview(
                        tutor=tutor.user,
                        reviewer=random.choice(studentProfiles).user,
                        comment=self.faker.paragraph(),
                        rating=random.randint(1, 5)
                    )
                )
            TutorReview.objects.bulk_create(TUTOR_REVIEWS)
            print(f"Created 70 tutor reviews for tutor: {tutor.id}")

    def bulkCreateLessons(self):
        tutorProfiles = TutorProfile.objects.all()
        studentProfiles = StudentProfile.objects.all()
        hours = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3]

        for tutor in tutorProfiles:
            LESSONS = []
            for i in range(40):
                hoursTaught = random.choice(hours)
                LESSONS.append(
                    Lesson(
                        tutor=tutor,
                        student=random.choice(studentProfiles),
                        hoursTaught=hoursTaught,
                        points=random.randint(0, 10),
                        amount=hoursTaught * float(tutor.chargeRate)
                    )
                )
            Lesson.objects.bulk_create(LESSONS)
            print(f"Created 40 tutor reviews for tutor: {tutor.id}")
