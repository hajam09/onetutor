import random
import string

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import BaseModel
from core.models import Component


def generateRandomString():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


class Qualification(models.TextChoices):
    DOCTORATE = 'DOCTORATE', _('Doctorate')
    MASTER_DEGREE = 'MASTER_DEGREE', _('Master Degree')
    BACHELOR_DEGREE = 'BACHELOR_DEGREE', _('Bachelor Degree')
    FOUNDATION_DEGREE = 'FOUNDATION_DEGREE', _('Foundation Degree')
    DIPLOMA = 'DIPLOMA', _('Diploma')
    IB = 'IB', _('International Baccalaureate (IB)')
    A_LEVEL = 'A_LEVEL', _('A-level')
    GCSE = 'GCSE', _('GCSE')
    KS3 = 'KS3', _('KS3')
    KS2 = 'KS2', _('KS2')
    KS1 = 'KS1', _('KS1')
    MENTORING = 'MENTORING', _('Mentoring')
    OTHER = 'OTHER', _('Other')


class TutorProfile(BaseModel):
    id = models.CharField(primary_key=True, default=generateRandomString, unique=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutorProfile')
    summary = models.CharField(max_length=256)
    about = models.TextField()
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()
    features = models.ManyToManyField(Component, blank=True, related_name='features')
    clearanceLevels = models.ManyToManyField(Component, blank=True, related_name='clearanceLevels')
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='tutor-profile-idx-user'),
        ]
        verbose_name_plural = 'TutorProfile'


class StudentProfile(BaseModel):
    id = models.CharField(primary_key=True, default=generateRandomString, unique=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentProfile')
    about = models.TextField()
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='children')

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='student-profile-idx-user'),
        ]
        verbose_name_plural = 'StudentProfile'


class ParentProfile(BaseModel):
    id = models.CharField(primary_key=True, default=generateRandomString, unique=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parentProfile')
    code = models.CharField(max_length=8, default=generateRandomString, editable=False, unique=True)
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='parent-profile-idx-user'),
        ]
        verbose_name_plural = 'ParentProfile'


class Education(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    schoolName = models.CharField(max_length=256, blank=True, null=True)
    qualification = models.CharField(max_length=256, blank=True, null=True)
    startDate = models.DateField(blank=True, null=True)
    endDate = models.DateField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='education-idx-user'),
        ]
        verbose_name_plural = 'Education'


class TutorQualification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userQualification')
    subject = models.CharField(max_length=256)
    qualification = models.CharField(max_length=64, choices=Qualification.choices, default=Qualification.OTHER)
    grade = models.CharField(max_length=16)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='qualification-idx-user'),
            models.Index(fields=['subject'], name='qualification-idx-subject'),
        ]
        verbose_name_plural = 'TutorQualification'


class SubjectOffered(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userSubjectsOffered')
    subject = models.CharField(max_length=256)
    qualification = models.CharField(max_length=64, choices=Qualification.choices, default=Qualification.OTHER)
    price = models.PositiveSmallIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='subject-offered-idx-user'),
            models.Index(fields=['subject'], name='subject-offered-idx-subject'),
        ]
        verbose_name_plural = 'SubjectOffered'
