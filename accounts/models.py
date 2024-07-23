from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    createdDateTime = models.DateTimeField(default=timezone.now)
    modifiedDateTime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GetInTouch(BaseModel):
    fullName = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    subject = models.CharField(max_length=256)
    message = models.TextField()

    class Meta:
        verbose_name_plural = 'GetInTouch'
