from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
import jsonfield
import uuid

class TutorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	secondary_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	summary = models.CharField(max_length=128)
	about = models.TextField()
	location = jsonfield.JSONField()
	education = jsonfield.JSONField()
	subjects = models.CharField(max_length=8192)
	availability = jsonfield.JSONField()
	profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True, default='profilepicture/defaultimg/default-profile-picture.jpg')

	class Meta:
		verbose_name_plural = "TutorProfiles"

class StudentProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	location = jsonfield.JSONField()# not implemented at the moment
	subjects = models.CharField(max_length=8192)
	profilePicture = models.ImageField(upload_to='profilepicture', blank=True, null=True)# not implemented at the moment

	class Meta:
		verbose_name_plural = "StudentProfiles"

class Subject(models.Model):
	name = models.CharField(max_length=64)

	class Meta:
		verbose_name_plural = "Subjects"
		ordering = ('name',)

	def __str__ (self):
		return str(self.id) + " - " + self.name

class Countries(models.Model):
	alpha = models.CharField(max_length=4)
	name = models.CharField(max_length=64)

	class Meta:
		verbose_name_plural = "Countries"
		ordering = ('name',)

	def __str__ (self):
		return str(self.id) + " - " + self.alpha + " - " + self.name

class SocialConnection(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	twitter = models.CharField(max_length=128, blank=True)
	facebook = models.CharField(max_length=128, blank=True)
	google = models.CharField(max_length=128, blank=True)
	linkedin = models.CharField(max_length=128, blank=True)

	class Meta:
		verbose_name_plural = "SocialConnection"

class UserSession(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	device_type = models.CharField(max_length=256)
	location = models.CharField(max_length=1024)
	ip_address = models.GenericIPAddressField()
	login_time = models.DateTimeField(default=datetime.now)
	allowed = models.BooleanField(default=True)

	class Meta:
		verbose_name_plural = "UserSessions"