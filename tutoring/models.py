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

class Availability(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name='availability')
    sundayMorning = models.BooleanField(default=False)
    sundayAfternoon = models.BooleanField(default=False)
    sundayEvening = models.BooleanField(default=False)
    mondayMorning = models.BooleanField(default=False)
    mondayAfternoon = models.BooleanField(default=False)
    mondayEvening = models.BooleanField(default=False)
    tuesdayMorning = models.BooleanField(default=False)
    tuesdayAfternoon = models.BooleanField(default=False)
    tuesdayEvening = models.BooleanField(default=False)
    wednesdayMorning = models.BooleanField(default=False)
    wednesdayAfternoon = models.BooleanField(default=False)
    wednesdayEvening = models.BooleanField(default=False)
    thursdayMorning = models.BooleanField(default=False)
    thursdayAfternoon = models.BooleanField(default=False)
    thursdayEvening = models.BooleanField(default=False)
    fridayMorning = models.BooleanField(default=False)
    fridayAfternoon = models.BooleanField(default=False)
    fridayEvening = models.BooleanField(default=False)
    saturdayMorning = models.BooleanField(default=False)
    saturdayAfternoon = models.BooleanField(default=False)
    saturdayEvening = models.BooleanField(default=False)

    def getAvailability(self):
        monday = {
            "morning": self.mondayMorning,
            "afternoon": self.mondayAfternoon,
            "evening": self.mondayEvening
        }

        tuesday = {
            "morning": self.tuesdayMorning,
            "afternoon": self.tuesdayAfternoon,
            "evening": self.tuesdayEvening
        }

        wednesday = {
            "morning": self.wednesdayMorning,
            "afternoon": self.wednesdayAfternoon,
            "evening": self.wednesdayEvening
        }

        thursday = {
            "morning": self.thursdayMorning,
            "afternoon": self.thursdayAfternoon,
            "evening": self.thursdayEvening
        }

        friday = {
            "morning": self.fridayMorning,
            "afternoon": self.fridayAfternoon,
            "evening": self.fridayEvening
        }

        saturday = {
            "morning": self.saturdayMorning,
            "afternoon": self.saturdayAfternoon,
            "evening": self.saturdayEvening
        }

        sunday = {
            "morning": self.sundayMorning,
            "afternoon": self.sundayAfternoon,
            "evening": self.sundayEvening
        }

        schedule = {
            "sunday": sunday,
            "monday": monday,
            "tuesday": tuesday,
            "wednesday": wednesday,
            "thursday": thursday,
            "friday": friday,
            "saturday": saturday
        }

        return schedule


class QuestionAnswer(models.Model):
    subject = models.CharField(max_length=1024)
    question = models.TextField()
    answer = models.TextField(null=True, default='Not answered yet.')
    questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner")  # user who asked the question
    answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer")  # user who is being asked the question (tutor)
    likes = models.ManyToManyField(User, related_name='questionAnswerLikes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='questionAnswerDislikes', blank=True)
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
    likes = models.ManyToManyField(User, related_name='questionAnswerCommentLikes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='questionAnswerCommentDislikes', blank=True)
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
    likes = models.ManyToManyField(User, related_name="tutorReviewLikes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="tutorReviewDislikes", blank=True)
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
