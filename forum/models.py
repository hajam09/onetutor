from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=512)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ('name',)

    def __str__(self):
        return self.name


class Community(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    url = models.CharField(max_length=512)
    tags = models.CharField(max_length=2048)
    description = models.TextField()
    createdAt = models.DateTimeField(default=datetime.now)
    likes = models.ManyToManyField(User, related_name='communityLikes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='communityDislikes', blank=True)
    banner = models.ImageField(upload_to='community-banner/', blank=True, null=True)
    logo = models.ImageField(upload_to='community-logo/', blank=True, null=True, default='community-logo/default-community-logo.jpg')
    members = models.ManyToManyField(User, related_name='communityMembers', blank=True)

    class Meta:
        verbose_name_plural = "Communities"


class Forum(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='forums')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    url = models.CharField(max_length=512)
    description = models.TextField(blank=True, null=True)
    createdAt = models.DateTimeField(default=datetime.now)
    anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='forumLikes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='forumDislikes', blank=True)
    image = models.ImageField(upload_to='forum-image/', blank=True, null=True)
    watchers = models.ManyToManyField(User, related_name='forumWatchers', blank=True)

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
        verbose_name_plural = "Forums"


class ForumComment(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='forumComments')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    createdAt = models.DateTimeField(default=datetime.now)
    anonymous = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    reply = models.ForeignKey('ForumComment', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='forumCommentLikes', blank=True, null=True)
    dislikes = models.ManyToManyField(User, related_name='forumCommentDislikes', blank=True, null=True)

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
        verbose_name_plural = "ForumComment"
