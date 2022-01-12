from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

from accounts.models import StudentProfile, TutorProfile

User = get_user_model()

# Create your models here.

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']

    def getFirstPersonProfilePicture(self):
        try:
            profile = self.first_person.tutorProfile
        except TutorProfile.DoesNotExist:
            profile = None

        if profile is None:
            try:
                profile = self.first_person.studentProfile
            except StudentProfile.DoesNotExist:
                profile = None

        if profile is None:
            return "https://bootdey.com/img/Content/avatar/avatar1.png"

        return profile.profilePicture.url

    def getSecondPersonProfilePicture(self):
        try:
            profile = self.second_person.tutorProfile
        except TutorProfile.DoesNotExist:
            profile = None

        if profile is None:
            try:
                profile = self.second_person.studentProfile
            except StudentProfile.DoesNotExist:
                profile = None

        if profile is None:
            return "https://bootdey.com/img/Content/avatar/avatar1.png"

        return profile.profilePicture.url


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='threadMessages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def getUserProfilePicture(self):
        try:
            profile = self.user.tutorProfile
        except TutorProfile.DoesNotExist:
            profile = None

        if profile is None:
            try:
                profile = self.user.studentProfile
            except StudentProfile.DoesNotExist:
                profile = None

        if profile is None:
            return "https://bootdey.com/img/Content/avatar/avatar1.png"

        return profile.profilePicture.url
