from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# class BaseComment(models.Model):
# 	creator = models.ForeignKey(User, on_delete=models.CASCADE)
# 	comment = models.TextField()
# 	likes = models.ManyToManyField(User, related_name='likes')
# 	dislikes = models.ManyToManyField(User, related_name='dislikes')
# 	date = models.DateTimeField(default=datetime.now)
# 	edited = models.BooleanField(default=False)


class QuestionAnswer(models.Model):
    subject = models.CharField(max_length=1024)
    question = models.TextField()
    answer = models.TextField(null=True, default='Not answered yet.')
    questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner")  # user who asked the question
    answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer")  # user who is being asked the question (tutor)
    likes = models.ManyToManyField(User, related_name='questionAnswerLikes', blank=True, null=True)
    dislikes = models.ManyToManyField(User, related_name='questionAnswerDislikes', blank=True, null=True)
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

    def questionAnswerThreadUrl(self):
        return reverse('tutoring:question-answer-thread', kwargs={'questionId': self.id})


class QuestionAnswerComment(models.Model):
    questionAnswer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    likes = models.ManyToManyField(User, related_name='questionAnswerCommentLikes', blank=True, null=True)
    dislikes = models.ManyToManyField(User, related_name='questionAnswerCommentDislikes', blank=True, null=True)
    date = models.DateTimeField(default=datetime.now)
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
        verbose_name_plural = "QuestionAnswerComments"


class TutorReview(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutorReviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    date = models.DateTimeField(default=datetime.now)
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    likes = models.ManyToManyField(User, related_name="tutorReviewLikes", blank=True, null=True)
    dislikes = models.ManyToManyField(User, related_name="tutorReviewDislikes", blank=True, null=True)
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
