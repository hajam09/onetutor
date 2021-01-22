from django.db import models
from django.contrib.auth.models import User
import datetime

class Room(models.Model):
	name = models.CharField(max_length=1024)
	participant = models.ManyToManyField(User, blank=True, related_name='room_participant')

class Message(models.Model):
	room = models.ForeignKey(Room, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="message_creator")
	message = models.TextField()
	date = models.DateTimeField(default=datetime.datetime.now)
	deleted = models.BooleanField(default=False)