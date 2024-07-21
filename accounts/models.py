import random
import string

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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


class BaseModel(models.Model):
    createdDateTime = models.DateTimeField(default=timezone.now)
    modifiedDateTime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TutorProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutorProfile')
    url = models.UUIDField(default=generateRandomString, editable=False, unique=True)
    summary = models.CharField(max_length=256)
    about = models.TextField()
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()
    features = ArrayField(models.CharField(max_length=8192), blank=True, related_name='features')
    verified = models.BooleanField(default=False)
    trustedBySchool = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='tutor-profile-idx-user'),
            models.Index(fields=['url'], name='tutor-profile-idx-url'),
        ]
        verbose_name_plural = 'TutorProfile'


class StudentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentProfile')
    url = models.UUIDField(default=generateRandomString, editable=False, unique=True)
    about = models.TextField()
    subjects = ArrayField(models.CharField(max_length=8192), blank=True, related_name='subjects')
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='children')

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='student-profile-idx-user'),
            models.Index(fields=['url'], name='student-profile-idx-url'),
        ]
        verbose_name_plural = 'StudentProfile'


class ParentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parentProfile')
    url = models.UUIDField(default=generateRandomString, editable=False, unique=True)
    code = models.CharField(max_length=8, default=generateRandomString, editable=False, unique=True)
    picture = models.ImageField(blank=True, null=True, upload_to='profile-picture')
    dateOfBirth = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='parent-profile-idx-user'),
            models.Index(fields=['url'], name='parent-profile-idx-url'),
        ]
        verbose_name_plural = 'ParentProfile'


class Education(models.Model):
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
            models.Index(fields=['user'], name='tutor-qualification-idx-user'),
            models.Index(fields=['subject'], name='tutor-qualification-idx-subject'),
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


class GetInTouch(BaseModel):
    fullName = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    subject = models.CharField(max_length=256)
    message = models.TextField()

    class Meta:
        verbose_name_plural = 'GetInTouch'
