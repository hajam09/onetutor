from django.contrib.auth.models import User
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=1024)
    participant = models.ManyToManyField(User, blank=True, related_name='room_participant')


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_creator")
    message = models.TextField()
    date = models.TimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    seen = models.BooleanField(default=False)
