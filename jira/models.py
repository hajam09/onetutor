from django.db import models
from django.contrib.auth.models import User
import datetime

class Ticket(models.Model):
	url = models.CharField(max_length=1024)
	project = models.CharField(max_length=1024)
	issue_type = models.CharField(max_length=1024)
	reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reporter")
	assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignee")
	summary = models.CharField(max_length=2048)
	description = models.TextField()
	points = models.IntegerField()
	created_date = models.DateField(default=datetime.date.today)
	status = models.CharField(max_length=16, default='None')
	priority = models.CharField(max_length=16, default='None')

	class Meta:
		verbose_name_plural = "Ticket"