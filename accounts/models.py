import os
import random
import uuid

import jsonfield
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from onetutor import settings
from tutoring.models import Component


def getRandomImageForAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


class TutorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutorProfile')
    secondaryKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    summary = models.CharField(max_length=128, blank=True, null=True)
    about = models.TextField()
    location = jsonfield.JSONField(blank=True, null=True)
    subjects = models.CharField(max_length=8192, blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)
    chargeRate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    components = models.ManyToManyField(Component, related_name='tutorComponents', blank=True, limit_choices_to={'componentGroup__code': 'TUTOR_FEATURE'})

    class Meta:
        verbose_name_plural = "TutorProfiles"

    def getSubjectsAsList(self):
        return self.subjects.split(",")

    def getTutoringUrl(self):
        return reverse('tutoring:view-tutor-profile', kwargs={'tutorProfileKey': self.secondaryKey})

    def getTutorFeatureComponents(self):
        # regular use of components.all in template should work now because of the limit_choices_to and the validation from the TutorProfileForm
        return self.components.filter(componentGroup__code="TUTOR_FEATURE")

    def __str__(self):
        return "{} - {}".format(self.user.email, self.user.get_full_name())


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentProfile')
    secondaryKey = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    about = models.TextField()
    education = jsonfield.JSONField(blank=True, null=True)
    subjects = models.CharField(max_length=8192, blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)

    class Meta:
        verbose_name_plural = "StudentProfiles"

    def getSubjectsAsList(self):
        return self.subjects.split(",")


class Subject(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Subjects"
        ordering = ('name',)

    def __str__(self):
        return "{} - {}".format(self.id, self.name)


class Countries(models.Model):
    alpha = models.CharField(max_length=4)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ('name',)

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
