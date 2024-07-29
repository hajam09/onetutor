from django.contrib.auth.models import User
from django.db import models

from accounts.models import BaseModel


class ComponentGroup(BaseModel):
    name = models.CharField(max_length=2048, blank=True, null=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    colour = models.CharField(max_length=8, blank=True, null=True)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    adminOnly = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='component-group-idx-name'),
            models.Index(fields=['code'], name='component-group-idx-code'),
        ]
        verbose_name_plural = 'ComponentGroup'

    def __str__(self):
        return self.name


class Component(BaseModel):
    componentGroup = models.ForeignKey(ComponentGroup, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=2048, blank=True, null=True)
    code = models.CharField(max_length=2048, blank=True, null=True)
    colour = models.CharField(max_length=8, blank=True, null=True)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    adminOnly = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['componentGroup'], name='component-idx-componentGroup'),
            models.Index(fields=['name'], name='component-idx-name'),
            models.Index(fields=['code'], name='component-idx-code'),
        ]
        ordering = ['componentGroup', 'orderNo']
        verbose_name_plural = 'Component'

    def __str__(self):
        return self.name


class Availability(BaseModel):
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

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='availability-idx-user'),
        ]
        verbose_name_plural = 'Availability'


class Question(BaseModel):
    topic = models.CharField(max_length=1024)
    query = models.CharField(max_length=2048)
    asker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='askerQuestions')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorQuestions')
    likes = models.ManyToManyField(User, related_name='questionLikes')
    dislikes = models.ManyToManyField(User, related_name='questionDislikes')

    class Meta:
        indexes = [
            models.Index(fields=['asker'], name='question-idx-asker'),
            models.Index(fields=['tutor'], name='question-idx-tutor'),
        ]
        verbose_name_plural = 'TutorQuestion'

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


class Response(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='questionResponses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authorResponses')
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='responseLikes')
    dislikes = models.ManyToManyField(User, related_name='responseDislikes')

    class Meta:
        indexes = [
            models.Index(fields=['question'], name='response-idx-question'),
            models.Index(fields=['user'], name='response-idx-user'),
        ]
        verbose_name_plural = 'Response'

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
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorReviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewer')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    likes = models.ManyToManyField(User, related_name='tutorReviewLikes')
    dislikes = models.ManyToManyField(User, related_name='tutorReviewDislikes')

    class Meta:
        indexes = [
            models.Index(fields=['tutor'], name='tutor-review-idx-tutor'),
            models.Index(fields=['reviewer'], name='tutor-review-idx-reviewer'),
        ]
        verbose_name_plural = 'TutorReview'

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
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tutorLessons')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='studentLessons')
    hoursTaught = models.DecimalField(max_digits=4, decimal_places=2)
    points = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=5, decimal_places=2)  # amount = hoursTaught * tutor.chargeRate

    class Meta:
        indexes = [
            models.Index(fields=['tutor'], name='lesson-idx-tutor'),
            models.Index(fields=['student'], name='lesson-idx-student'),
        ]
        verbose_name_plural = 'Lesson'
