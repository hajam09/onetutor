import datetime

from django.contrib.auth.models import User
from django.db import models


class Sprint(models.Model):
    url = models.CharField(max_length=1024)
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=datetime.date.today)

    class Meta:
        verbose_name_plural = "Sprint"


class Ticket(models.Model):
    url = models.CharField(max_length=1024)
    project = models.CharField(max_length=1024)
    issueType = models.CharField(max_length=1024)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reporter")
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignee")
    summary = models.CharField(max_length=2048)
    description = models.TextField()
    points = models.IntegerField()
    createdDate = models.DateField(default=datetime.date.today)
    modifiedDate = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=16, default='None')
    priority = models.CharField(max_length=16, default='None')
    watchers = models.ManyToManyField(User, blank=True, related_name='watchers')
    sprint = models.ForeignKey(Sprint, models.SET_NULL, blank=True, null=True)
    subTask = models.ManyToManyField('Ticket', blank=True, related_name='subTasks')

    class Meta:
        verbose_name_plural = "Ticket"

    def __str__(self):
        return self.url


class TicketImage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='ticketImages')
    image = models.ImageField(upload_to='ticket-images/')

    class Meta:
        verbose_name_plural = "TicketImage"


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    likes = models.ManyToManyField(User, related_name='ticketCommentLikes')
    dislikes = models.ManyToManyField(User, related_name='ticketCommentDislikes')
    date = models.DateTimeField(default=datetime.datetime.now)
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
        verbose_name_plural = "TicketComment"
