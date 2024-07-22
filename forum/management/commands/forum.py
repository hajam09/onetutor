import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from forum.models import Thread, Comment


class Command(BaseCommand):
    NUMBER_OF_USERS = 100
    NUMBER_OF_THREADS = 500
    PASSWORD = 'admin'

    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    @transaction.atomic
    def handle(self, *args, **options):
        self.bulkCreateUsersAndProfiles()
        self.bulkCreateThreads()
        self.bulkCreateThreadComments()

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with random data'))

    def _email(self, first_name, last_name):
        return f'{first_name}.{last_name}@{self.faker.free_email_domain()}'

    def bulkCreateUsersAndProfiles(self):
        print(f'Attempting to create {self.NUMBER_OF_USERS} User objects.')

        users = []
        for _ in range(self.NUMBER_OF_USERS):
            if _ % 10 == 0:
                print(f'Processed {_} users out of {self.NUMBER_OF_USERS}.')
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            email = self._email(first_name.lower(), last_name.lower())

            user = User()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = self.faker.user_name()
            user.set_password(Command.PASSWORD)
            users.append(user)
        User.objects.bulk_create(users)
        return

    def bulkCreateThreads(self):
        print(f'Attempting to create {self.NUMBER_OF_THREADS} Thread objects.')
        users = User.objects.all()

        threads = []
        for _ in range(self.NUMBER_OF_THREADS):
            if _ % 10 == 0:
                print(f'Processed {_} threads out of {self.NUMBER_OF_THREADS}.')
            creator = random.choice(users)
            createdDateTime = timezone.now() - timedelta(days=random.randint(0, 180))
            thread = Thread(
                creator=creator,
                title=self.faker.sentence(nb_words=6),
                description=self.faker.paragraph(nb_sentences=3),
                anonymous=random.choice([True, False]),
                createdDateTime=createdDateTime
            )
            threads.append(thread)

        Thread.objects.bulk_create(threads)
        users = list(users)

        for thread in Thread.objects.all():
            thread.likes.add(*random.sample(users, random.randint(0, 50)))
            thread.dislikes.add(*random.sample(users, random.randint(0, 50)))
            thread.watchers.add(*random.sample(users, random.randint(0, 50)))
        return

    def bulkCreateThreadComments(self):
        print(f'Attempting to create Comment objects.')
        users = User.objects.all()

        for thread in Thread.objects.all():
            comments = []
            numberOfComments = random.randint(15, 100)
            for _ in range(numberOfComments):
                if _ % 10 == 0:
                    print(f'Processed {_} comments out of {numberOfComments} for thread {thread.id}.')
                creator = random.choice(users)
                createdDateTime = thread.createdDateTime + timedelta(days=random.randint(0, 180))
                comment = Comment(
                    thread=thread,
                    creator=creator,
                    content=self.faker.paragraph(nb_sentences=2),
                    anonymous=random.choice([True, False]),
                    createdDateTime=createdDateTime
                )
                comments.append(comment)
            Comment.objects.bulk_create(comments)

        users = list(users)
        for comment in Comment.objects.all():
            comment.likes.add(*random.sample(users, random.randint(0, 50)))
            comment.dislikes.add(*random.sample(users, random.randint(0, 50)))
        return
