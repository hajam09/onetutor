import os
import random
import string
import uuid

from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from onetutor import settings


def generateAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


def generateParentCode():
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class Qualification(models.TextChoices):
    DOCTORATE = "DOCTORATE", _("Doctorate")
    MASTER_DEGREE = "MASTER_DEGREE", _("Master Degree")
    BACHELOR_DEGREE = "BACHELOR_DEGREE", _("Bachelor Degree")
    FOUNDATION_DEGREE = "FOUNDATION_DEGREE", _("Foundation Degree")
    DIPLOMA = "DIPLOMA", _("Diploma")
    IB = "IB", _("International Baccalaureate (IB)")
    A_LEVEL = "A_LEVEL", _("A-level")
    GCSE = "GCSE", _("GCSE")
    KS3 = "KS3", _("KS3")
    KS2 = "KS2", _("KS2")
    KS1 = "KS1", _("KS1")
    MENTORING = "MENTORING", _("Mentoring")
    OTHER = "OTHER", _("Other")


class BaseModel(models.Model):
    createdDateTime = models.DateTimeField(default=timezone.now)
    modifiedDateTime = models.DateTimeField(auto_now=True)
    reference = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        abstract = True


class ComponentGroup(BaseModel):
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    icon = models.CharField(max_length=2048, blank=True, null=True)
    colour = ColorField(default="#FF0000")
    orderNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "ComponentGroup"

    def __str__(self):
        return self.internalKey


class Component(BaseModel):
    componentGroup = models.ForeignKey(ComponentGroup, on_delete=models.CASCADE, related_name="components")
    internalKey = models.CharField(max_length=2048, blank=True, null=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    icon = models.CharField(max_length=2048, blank=True, null=True)
    colour = ColorField(default="#FF0000")
    orderNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        ordering = ["componentGroup", "orderNo"]
        verbose_name_plural = "Component"

    def __str__(self):
        return f"{self.componentGroup.internalKey} - {self.internalKey}"


class TutorProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutorProfile")
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    summary = models.CharField(max_length=256)
    about = models.TextField()
    picture = models.ImageField(default=generateAvatar, upload_to="profile-picture")
    price = models.PositiveSmallIntegerField()
    features = models.ManyToManyField(Component, blank=True, related_name="features")  # TUTOR_FEATURE
    verified = models.BooleanField(default=False)
    trustedBySchool = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "TutorProfile"

    def getModelName(self):
        return self.__class__.__name__


class StudentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="studentProfile")
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    about = models.TextField()
    subjects = models.CharField(max_length=8192, blank=True, null=True)
    picture = models.ImageField(default=generateAvatar, upload_to="profile-picture")
    dateOfBirth = models.DateField(blank=True, null=True)
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="children")

    class Meta:
        verbose_name_plural = "StudentProfile"

    def getModelName(self):
        return self.__class__.__name__

    def getSubjectsAsList(self):
        return self.subjects.split("&#44;")


class ParentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parentProfile")
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=8, default=generateParentCode, editable=False, unique=True)
    dateOfBirth = models.DateField(blank=True, null=True)
    picture = models.ImageField(default=generateAvatar, upload_to="profile-picture")

    class Meta:
        verbose_name_plural = "ParentProfile"

    def getModelName(self):
        return self.__class__.__name__


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="education")
    schoolName = models.CharField(max_length=256, blank=True, null=True)
    qualification = models.CharField(max_length=256, blank=True, null=True)
    startDate = models.DateField(blank=True, null=True)
    endDate = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Education"


class TutorQualification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userQualification")
    subject = models.CharField(max_length=256)
    qualification = models.CharField(max_length=64, choices=Qualification.choices, default=Qualification.OTHER)
    grade = models.CharField(max_length=16)

    class Meta:
        verbose_name_plural = "TutorQualification"


class SubjectOffered(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userSubjectsOffered")
    subject = models.CharField(max_length=256)
    qualification = models.CharField(max_length=64, choices=Qualification.choices, default=Qualification.OTHER)
    price = models.PositiveSmallIntegerField()

    class Meta:
        verbose_name_plural = "SubjectOffered"


class GetInTouch(BaseModel):
    fullName = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    subject = models.CharField(max_length=256, blank=True, null=True)
    message = models.TextField()

    class Meta:
        verbose_name_plural = "GetInTouch"
