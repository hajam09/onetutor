from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ipAddress = models.GenericIPAddressField(null=True, blank=True)
    userAgent = models.CharField(max_length=1024, null=True, blank=True)
    sessionKey = models.CharField(max_length=32, null=True, blank=True)
    dateTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "UserSession"


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    loginTime = models.DateTimeField(auto_now_add=True)
    logoutTime = models.DateTimeField(default=datetime.max)

    class Meta:
        verbose_name_plural = "UserLogin"
