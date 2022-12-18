from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from accounts.models import BaseModel, TutorProfile, StudentProfile, Component


class Availability(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name="availability")
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

    class Meta:
        verbose_name_plural = "Availability"

    def getAvailability(self):
        morning = {
            "sunday": self.sundayMorning,
            "monday": self.mondayMorning,
            "tuesday": self.tuesdayMorning,
            "wednesday": self.wednesdayMorning,
            "thursday": self.thursdayMorning,
            "friday": self.fridayMorning,
            "saturday": self.saturdayMorning
        }

        afternoon = {
            "sunday": self.sundayAfternoon,
            "monday": self.mondayAfternoon,
            "tuesday": self.tuesdayAfternoon,
            "wednesday": self.wednesdayAfternoon,
            "thursday": self.thursdayAfternoon,
            "friday": self.fridayAfternoon,
            "saturday": self.saturdayAfternoon
        }

        evening = {
            "sunday": self.sundayEvening,
            "monday": self.mondayEvening,
            "tuesday": self.tuesdayEvening,
            "wednesday": self.wednesdayEvening,
            "thursday": self.thursdayEvening,
            "friday": self.fridayEvening,
            "saturday": self.saturdayEvening
        }

        schedule = {
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
        }

        return schedule


class QuestionAnswer(BaseModel):
    subject = models.CharField(max_length=1024)
    question = models.TextField()
    answer = models.TextField(default="Not answered yet.")
    questioner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questioner")
    answerer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="answerer")
    likes = models.ManyToManyField(User, blank=True, related_name="questionAnswerLikes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="questionAnswerDislikes")

    class Meta:
        verbose_name_plural = "QuestionAnswer"

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

    def questionAnswerThreadUrl(self):
        return reverse('tutoring:question-answer-thread', kwargs={'questionId': self.id})


class QuestionAnswerComment(BaseModel):
    questionAnswer = models.ForeignKey(QuestionAnswer, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    likes = models.ManyToManyField(User, blank=True, related_name="questionAnswerCommentLikes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="questionAnswerCommentDislikes")

    class Meta:
        verbose_name_plural = "QuestionAnswerComment"

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


class TutorReview(BaseModel):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutorReviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    likes = models.ManyToManyField(User, blank=True, related_name="tutorReviewLikes")
    dislikes = models.ManyToManyField(User, blank=True, related_name="tutorReviewDislikes")

    class Meta:
        verbose_name_plural = "TutorReview"

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


class Lesson(BaseModel):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.SET_NULL, null=True, related_name="tutorLessons")
    student = models.ForeignKey(StudentProfile, on_delete=models.SET_NULL, null=True, related_name="studentLessons")
    hoursTaught = models.DecimalField(max_digits=4, decimal_places=2)
    points = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=5, decimal_places=2)  # amount = hoursTaught * tutor.chargeRate

    class Meta:
        verbose_name_plural = "Lesson"


class Payment(BaseModel):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payerPayment")
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payeePayment")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="lessonPayment")
    method = models.ForeignKey(Component, on_delete=models.SET_NULL, null=True, related_name="method")  # PAYMENT_METHOD

    class Meta:
        verbose_name_plural = "Payment"
