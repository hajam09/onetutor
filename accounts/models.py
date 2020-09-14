from django.db import models
from django.contrib.auth.models import User
import jsonfield

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	userType = models.CharField(max_length=8)
	summary = models.CharField(max_length=128)
	about = models.CharField(max_length=8192)
	location = jsonfield.JSONField()# not implemented at the moment
	education = jsonfield.JSONField()
	subjects = models.CharField(max_length=8192)
	availability = jsonfield.JSONField()# not implemented at the moment
	profilePicture = models.ImageField(upload_to='profilepicture', blank=True)# not implemented at the moment