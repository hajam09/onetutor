from django.db import models
from django.contrib.auth.models import User
import jsonfield, uuid

class TutorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	secondary_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	userType = models.CharField(max_length=8)
	summary = models.CharField(max_length=128)
	about = models.TextField()
	location = jsonfield.JSONField()
	education = jsonfield.JSONField()
	subjects = models.CharField(max_length=8192)
	availability = jsonfield.JSONField()
	profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True)

class StudentProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	userType = models.CharField(max_length=8)
	location = jsonfield.JSONField()# not implemented at the moment
	subjects = models.CharField(max_length=8192)
	profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True)# not implemented at the moment

class Subject(models.Model):
	name = models.CharField(max_length=64)

	def __str__ (self):
		return str(self.id) + " - " + self.name

class Countries(models.Model):
	alpha = models.CharField(max_length=4)
	name = models.CharField(max_length=64)

	def __str__ (self):
		return str(self.id) + " - " + self.alpha + " - " + self.name