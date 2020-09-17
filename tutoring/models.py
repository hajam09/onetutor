from django.db import models
from django.contrib.auth.models import User

class QuestionAnswer(models.Model):
	subject = models.CharField(max_length=1024)
	question = models.TextField()
	answer = models.TextField(null=True)
	questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner") # user who asked the question
	answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer") # user who is being asked the question (tutor)
	likes = models.ManyToManyField(User, related_name='likes')
	dislikes = models.ManyToManyField(User, related_name='dislikes')