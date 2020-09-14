from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from onetutor.operations import generalOperations

DEFAULT_AVATAR = "https://dummyimage.com/500x500"


class ThreadManager(models.Manager):

    def byUser(self, **kwargs):
        user = kwargs.get("user")
        lookup = Q(firstParticipant=user) | Q(secondParticipant=user)
        return self.get_queryset().filter(lookup).distinct()


class Thread(models.Model):
    firstParticipant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threadFirstParticipant")
    secondParticipant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threadSecondParticipant")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        verbose_name_plural = "Thread"
        unique_together = ["firstParticipant", "secondParticipant"]

    def getFirstPersonProfilePicture(self):
        profile = generalOperations.getProfileForUser(self.firstParticipant)

        if profile is None:
            return DEFAULT_AVATAR

        return profile.picture.url

    def getSecondPersonProfilePicture(self):
        profile = generalOperations.getProfileForUser(self.secondParticipant)

        if profile is None:
            return DEFAULT_AVATAR

        return profile.picture.url


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="threadMessages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "ChatMessage"

    def getUserProfilePicture(self):
        profile = generalOperations.getProfileForUser(self.user)

        if profile is None:
            return DEFAULT_AVATAR

        return profile.picture.url
