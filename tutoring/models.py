from datetime import datetime

from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
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

    def __str__(self):
        return self.user.email


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


class Lesson(models.Model):
    tutor = models.ForeignKey("accounts.TutorProfile", on_delete=models.SET_NULL, null=True, related_name="tutorLessons")
    student = models.ForeignKey("accounts.StudentProfile", on_delete=models.SET_NULL, null=True, related_name="studentLessons")
    hoursTaught = models.DecimalField(max_digits=4, decimal_places=2)
    dateTime = models.DateTimeField(auto_now_add=True)
    points = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10)])
    amount = models.DecimalField(max_digits=5, decimal_places=2)  # amount = hoursTaught * tutor.chargeRate


class Feature(models.Model):
    name = models.CharField(max_length=1024)
    code = models.CharField(max_length=1024)
    colour = ColorField(default='#FF0000')

    def __str__(self):
        return self.name


class ComponentGroup(models.Model):
    internalKey = models.CharField(max_length=2048, blank=True, null=True)
    reference = models.CharField(max_length=2048, blank=True, null=True)
    languageKey = models.CharField(max_length=2048, blank=True, null=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    icon = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    colour = ColorField(default='#FF0000')
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "ComponentGroup"

    def __str__(self):
        return self.internalKey

    def getRelatedFeatureComponentByOrderNo(self):
        return self.components.all().order_by('orderNo')

    def getRelatedFeatureComponentByOrderNoForId(self):
        return ["features-{}".format(i.code) for i in self.components.all()]


class Component(models.Model):
    componentGroup = models.ForeignKey(ComponentGroup, on_delete=models.CASCADE, related_name="components")
    internalKey = models.CharField(max_length=2048, blank=True, null=True)
    reference = models.CharField(max_length=2048, blank=True, null=True)
    languageKey = models.CharField(max_length=2048, blank=True, null=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    icon = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    colour = ColorField(default='#FF0000')
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        ordering = ['componentGroup', 'orderNo']
        verbose_name_plural = "Component"

    def __str__(self):
        return self.internalKey


class Payment(models.Model):
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paymentPayer")
    payee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paymentPayee")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="paymentLesson")
    paymentComponent = models.ForeignKey(Component, on_delete=models.SET_NULL, null=True, related_name="paymentComponent", limit_choices_to={'componentGroup__code': 'PAYMENT_METHOD'})
    dateTime = models.DateTimeField(auto_now_add=True)

# class FeatureFlag(models.Model):
#     name = models.CharField(max_length=2048, blank=True, null=True)
#     enabledFl = models.BooleanField(default=False)
#     reference = models.CharField(max_length=2048, blank=True, null=True)
#     deleteFl = models.BooleanField(default=False)
#     versionNo = models.IntegerField(default=1, blank=True, null=True)
#     orderNo = models.IntegerField(default=1, blank=True, null=True)