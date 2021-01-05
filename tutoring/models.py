from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# class BaseComment(models.Model):
# 	creator = models.ForeignKey(User, on_delete=models.CASCADE)
# 	comment = models.TextField()
# 	likes = models.ManyToManyField(User, related_name='likes')
# 	dislikes = models.ManyToManyField(User, related_name='dislikes')
# 	date = models.DateTimeField(default=datetime.now)
# 	edited = models.BooleanField(default=False)

# 	class Meta:
# 		verbose_name_plural = "BaseComment"

class QuestionAnswer(models.Model):
	subject = models.CharField(max_length=1024)
	question = models.TextField()
	answer = models.TextField(null=True)
	questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner") # user who asked the question
	answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer") # user who is being asked the question (tutor)
	likes = models.ManyToManyField(User, related_name='likes')
	dislikes = models.ManyToManyField(User, related_name='dislikes')
	date = models.DateTimeField(default=datetime.now)

	class Meta:
		verbose_name_plural = "QuestionAnswer"

class QAComment(models.Model):
	question_answer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	comment = models.TextField()
	likes = models.ManyToManyField(User, related_name='qacomment_likes')
	dislikes = models.ManyToManyField(User, related_name='qacomment_dislikes')
	date = models.DateTimeField(default=datetime.now)
	edited = models.BooleanField(default=False)

	class Meta:
		verbose_name_plural = "QAComments"