import datetime
import os
import random
import uuid

from colorfield.fields import ColorField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from onetutor import settings
from tutoring.models import Component


def sprintEndDate(today):
    return today() + datetime.timedelta(days=14)

def getRandomImageForAvatar():
    return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


class Sprint(models.Model):
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=sprintEndDate(datetime.date.today))
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sprint"


class Project(models.Model):
    name = models.CharField(max_length=2048)
    code = models.CharField(max_length=2048, unique=True)
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    url = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    lead = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, limit_choices_to={'componentGroup__code': 'PROJECT_STATUS'})
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=datetime.datetime.max)
    createdDate = models.DateField(default=datetime.date.today)
    isPrivate = models.BooleanField(default=False)
    description = models.TextField()
    members = models.ManyToManyField(User, blank=True, related_name='_projectMembers')
    watchers = models.ManyToManyField(User, blank=True, related_name='_projectWatchers')
    icon = models.ImageField(upload_to='project-icons/')
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    def getProjectUrl(self):
        return reverse('jira2:project-page', kwargs={'url': self.url})


class Board(models.Model):
    name = models.CharField(max_length=2048)
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    url = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    sprint = models.ForeignKey(Sprint, null=True, blank=True, on_delete=models.SET_NULL)
    projects = models.ManyToManyField(Project, blank=True, related_name='_boardProjects')
    members = models.ManyToManyField(User, blank=True, related_name='_boardMembers')
    admins = models.ManyToManyField(User, blank=True, related_name='_boardAdmins')
    isPrivate = models.BooleanField(default=False)
    createdDttm = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)
    # location

    class Meta:
        verbose_name_plural = "Board"
        ordering = ['orderNo']

    def __str__(self):
        return self.name

    def getBoardUrl(self):
        return reverse('jira2:board-page', kwargs={'url': self.url})


class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='boardColumns')
    name = models.CharField(max_length=2048, blank=True, null=True)
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    colour = ColorField(default='#FF0000')
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Column"
        ordering = ['orderNo']

    def __str__(self):
        return self.name


class Label(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='boardLabels')
    name = models.CharField(max_length=2048, blank=True, null=True)
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    colour = ColorField(default='#FF0000')
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Label"


class Ticket(models.Model):
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)  # PROJECT_CODE + PK
    summary = models.CharField(max_length=2048)
    fixVersion = models.CharField(max_length=2048)
    component = models.CharField(max_length=2048)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="_ticketAssignee")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="_ticketReporter")
    colour = ColorField(default='#FF0000')  # EPIC colour
    description = models.TextField()
    userImpact = models.TextField()
    technicalImpact = models.TextField()
    releaseImpact = models.TextField()
    automatedTestingReason = models.TextField()
    storyPoints = models.IntegerField()
    manDays = models.IntegerField()
    createdDttm = models.DateTimeField(auto_now_add=True)
    modifiedDttm = models.DateTimeField(auto_now=True)
    issueType = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, related_name='_ticketIssueType', limit_choices_to={'componentGroup__code': 'TICKET_ISSUE_TYPE'})
    securityLevel = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, related_name='_ticketSecurity', limit_choices_to={'componentGroup__code': 'TICKET_SECURITY'})
    status = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, related_name='_ticketStatus', limit_choices_to={'componentGroup__code': 'TICKET_STATUS'})
    priority = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, related_name='_ticketPriority', limit_choices_to={'componentGroup__code': 'TICKET_PRIORITY'})
    watchers = models.ManyToManyField(User, blank=True, related_name='_ticketWatchers')
    subTask = models.ManyToManyField('Ticket', blank=True, related_name='_ticketSubTask')
    label = models.ManyToManyField(Label, blank=True, related_name='_ticketLabels')
    board = models.ForeignKey(Board, null=True, on_delete=models.SET_NULL)
    column = models.ForeignKey(Column, null=True, on_delete=models.SET_NULL, related_name='_columnTickets')
    epic = models.ForeignKey('Ticket', null=True, on_delete=models.SET_NULL, related_name='_epicTickets')
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='_ticketCommentCreator')
    comment = models.TextField()
    likes = models.ManyToManyField(User, related_name='_ticketCommentLikes')
    dislikes = models.ManyToManyField(User, related_name='_ticketCommentDislikes')
    createdDttm = models.DateTimeField(auto_now_add=True)
    modifiedDttm = models.DateTimeField(auto_now=True)
    edited = models.BooleanField(default=False)
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='_ticketAttachments')
    image = models.ImageField(upload_to='ticket-images/')
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)


class DeveloperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='developerProfile')
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    jobTitle = models.CharField(max_length=2048, blank=True, null=True)
    department = models.CharField(max_length=2048, blank=True, null=True)
    profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomImageForAvatar)


class Team(models.Model):
    name = models.CharField(max_length=2048, blank=True, null=True)
    internalKey = models.CharField(max_length=2048, blank=True, null=True, unique=True)
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    members = models.ManyToManyField(User, related_name='_teamMembers')
    description = models.TextField()
    reference = models.CharField(max_length=2048, blank=True, null=True)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)
