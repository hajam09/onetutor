import random

from django.contrib.auth.models import User
from django.db import connection
from faker import Faker

from jira2.models import DeveloperProfile

all_tables = connection.introspection.table_names()

# CONSTANT VALUES
EMAIL_DOMAINS = ["@yahoo", "@gmail", "@outlook", "@hotmail"]
DOMAINS = [".co.uk", ".com", ".co.in", ".net", ".us"]
BOOLEAN = [True, False]

JOB_TITLE = ['Software Engineer', 'Project Owner', 'Project Manager', 'UX/UI Designer', 'Solutions Architect']


def createDeveloperProfile(limit=20, maxLimit=20):
    if limit == 0:
        return

    if 'jira2_developerprofile' not in all_tables:
        return

    currentCount = DeveloperProfile.objects.count()
    remaining = maxLimit - currentCount

    if currentCount > maxLimit:
        return

    BULK_USERS = []
    uniqueEmails = []

    for _ in range(remaining):
        fake = Faker()
        firstName = fake.unique.first_name()
        lastName = fake.unique.last_name()
        email = firstName.lower() + '.' + lastName.lower() + random.choice(EMAIL_DOMAINS) + random.choice(DOMAINS)
        password = 'RanDomPasWord56'

        BULK_USERS.append(
            User(username=email, email=email, password=password, first_name=firstName, last_name=lastName)
        )
        uniqueEmails.append(email)

    User.objects.bulk_create(BULK_USERS)
    createdUsers = User.objects.filter(email__in=uniqueEmails)
    DeveloperProfile.objects.bulk_create(
        [
            DeveloperProfile(user=i, jobTitle=random.choice(JOB_TITLE))
            for i in createdUsers
        ]
    )