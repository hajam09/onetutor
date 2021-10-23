import uuid

import jsonfield
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# TODO: Remove fields: location
class TutorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secondary_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    summary = models.CharField(max_length=128)
    about = models.TextField()
    location = jsonfield.JSONField()
    education = jsonfield.JSONField()
    subjects = models.CharField(max_length=8192)
    availability = jsonfield.JSONField()
    profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True, default='profilepicture/defaultimg/default-profile-picture.jpg')

    class Meta:
        verbose_name_plural = "TutorProfiles"

    def getSubjectsAsList(self):
        return self.subjects.split(",")

    def getTutoringUrl(self):
        return reverse('tutoring:view-tutor-profile', kwargs={'tutorProfileKey': self.secondary_key})


# TODO: Remove fields: location
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = jsonfield.JSONField()
    subjects = models.CharField(max_length=8192)
    profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True)  # not implemented at the moment

    class Meta:
        verbose_name_plural = "StudentProfiles"


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
