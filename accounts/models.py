import os
import random
import string
import uuid
from datetime import date

import jsonfield
from django.contrib.auth.models import User
from django.core.validators import BaseValidator
from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from onetutor import settings
from tutoring.models import Component


@deconstructible
class MinAgeValidator(BaseValidator):
    message = _("Age must be at least %(limit_value)d.")
    code = 'min_age'

    def calculateAge(self, born):
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def compare(self, a, b):
        return self.calculateAge(a) < b


def getRandomImageForAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


def getParentCode():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class TutorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutorProfile')
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    summary = models.CharField(max_length=128, blank=True, null=True)
    about = models.TextField()
    location = jsonfield.JSONField(blank=True, null=True)
    subjects = models.CharField(max_length=8192, blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)
    chargeRate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    features = models.ManyToManyField(Component, related_name='featuresComponents', blank=True, limit_choices_to={'componentGroup__code': 'TUTOR_FEATURE'})
    teachingLevels = models.ManyToManyField(Component, related_name='teachingComponent', blank=True, limit_choices_to={'componentGroup__code': 'EDUCATION_LEVEL'})  # store which education level(s) this tutor teaches.

    class Meta:
        verbose_name_plural = "TutorProfile"
        ordering = ['-id']
        indexes = [
            models.Index(fields=['url', ])
        ]

    def getSubjectsAsList(self):
        return self.subjects.split(",")

    def getTutoringUrl(self):
        return reverse('tutoring:view-tutor-profile', kwargs={'url': self.url})

    @property
    def getTutorRatingAsStars(self):
        tutorReviewsObjects = self.user.tutorReviews
        outOfPoints = tutorReviewsObjects.count() * 5
        sumOfRating = sum([i.rating for i in tutorReviewsObjects.all()])

        try:
            averageRating = sumOfRating * 5 / outOfPoints
            roundedRating = round(averageRating * 2) / 2
        except ZeroDivisionError:
            roundedRating = 0

        pureRating = int(roundedRating)
        decimalPart = roundedRating - pureRating
        finalScore = "+" * pureRating

        if decimalPart >= 0.75:
            finalScore += "+"
        elif decimalPart >= 0.25:
            finalScore += "_"
        # <i class="far fa-star"></i> for empty star
        return finalScore.replace('+', '<i class="fas fa-star"></i>').replace('_', '<i class="fas fa-star-half"></i>')

    def __str__(self):
        return "{} - {}".format(self.user.email, self.user.get_full_name())


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentProfile')
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    about = models.TextField()
    education = jsonfield.JSONField(blank=True, null=True)
    subjects = models.CharField(max_length=8192, blank=True, null=True)
    dateOfBirth = models.DateField(blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='studentsParent')

    class Meta:
        verbose_name_plural = "StudentProfile"
        indexes = [
            models.Index(fields=['url', ])
        ]

    def getSubjectsAsList(self):
        return self.subjects.split(",")


class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parentProfile')
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=8, default=getParentCode, editable=False, unique=True)
    dateOfBirth = models.DateField(validators=[MinAgeValidator(18)], blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)

    class Meta:
        verbose_name_plural = "ParentProfile"
        indexes = [
            models.Index(fields=['url', ])
        ]


class Subject(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Subject"
        ordering = ('name',)

    def __str__(self):
        return "{} - {}".format(self.id, self.name)


class Countries(models.Model):
    alpha = models.CharField(max_length=4)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name', ])
        ]

    def __str__(self):
        return "{} - {} - {}".format(self.id, self.alpha, self.name)


class SocialConnection(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    twitter = models.CharField(max_length=128, blank=True)
    facebook = models.CharField(max_length=128, blank=True)
    google = models.CharField(max_length=128, blank=True)
    linkedin = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name_plural = "SocialConnection"


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    schoolName = models.CharField(max_length=256, blank=True, null=True)
    qualification = models.CharField(max_length=256, blank=True, null=True)
    startDate = models.DateField(blank=True, null=True)
    endDate = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Education"


class GetInTouch(models.Model):
    fullName = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    subject = models.CharField(max_length=256, blank=True, null=True)
    message = models.TextField()
    dateTime = models.DateTimeField(auto_now_add=True, editable=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "GetInTouch"
