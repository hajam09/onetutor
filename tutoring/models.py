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
	answer = models.TextField(null=True, default='Not answered yet.')
	questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner") # user who asked the question
	answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer") # user who is being asked the question (tutor)
	likes = models.ManyToManyField(User, related_name='likes')
	dislikes = models.ManyToManyField(User, related_name='dislikes')
	date = models.DateTimeField(default=datetime.now)

	def like(self, request):
		if request.user not in self.likes.all():
			self.likes.add(request.user)
		else:
			self.likes.remove(request.user)

		if request.user in self.dislikes.all():
			self.dislikes.remove(request.user)

	def dislike(self, request):
		if request.user not in self.dislikes.all():
			self.dislikes.add(request.user)
		else:
			self.dislikes.remove(request.user)

		if request.user in self.likes.all():
			self.likes.remove(request.user)

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

	def increase_qa_comment_likes(self, request):
		if(request.user not in self.likes.all()):
			self.likes.add(request.user)
		else:
			self.likes.remove(request.user)

		if(request.user in self.dislikes.all()):
			self.dislikes.remove(request.user)

	def increase_qa_comment_dislikes(self, request):
		if(request.user not in self.dislikes.all()):
			self.dislikes.add(request.user)
		else:
			self.dislikes.remove(request.user)

		if(request.user in self.likes.all()):
			self.likes.remove(request.user)

	class Meta:
		verbose_name_plural = "QAComments"

class TutorReview(models.Model):
	tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
	reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
	date = models.DateTimeField(default=datetime.now)
	comment = models.TextField()
	rating = models.PositiveSmallIntegerField()
	likes = models.ManyToManyField(User, related_name="tutorReviewLikes")
	dislikes = models.ManyToManyField(User, related_name="tutorReviewDislikes")
	edited = models.BooleanField(default=False)

	def like(self, request):
		if request.user not in self.likes.all():
			self.likes.add(request.user)
		else:
			self.likes.remove(request.user)

		if request.user in self.dislikes.all():
			self.dislikes.remove(request.user)

	def dislike(self, request):
		if request.user not in self.dislikes.all():
			self.dislikes.add(request.user)
		else:
			self.dislikes.remove(request.user)

		if request.user in self.likes.all():
			self.likes.remove(request.user)

	class Meta:
		verbose_name_plural = "TutorReview"