from django.contrib.auth.models import User
from django.db import models

from accounts.models import BaseModel, generateRandomString


class Category(BaseModel):
    name = models.CharField(max_length=1024, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='category-idx-name'),
        ]
        verbose_name_plural = 'Category'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Thread(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=8, default=generateRandomString)
    description = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='threadLikes')
    dislikes = models.ManyToManyField(User, related_name='threadDislikes')
    watchers = models.ManyToManyField(User, related_name='threadWatchers')
    picture = models.ImageField(blank=True, null=True, upload_to='forum-image/')

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
        indexes = [
            models.Index(fields=['creator'], name='thread-idx-creator'),
            models.Index(fields=['title'], name='thread-idx-title'),
            models.Index(fields=['description'], name='thread-idx-description'),
        ]
        verbose_name_plural = 'Thread'


class Comment(BaseModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='threadComments')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='commentLikes')
    dislikes = models.ManyToManyField(User, related_name='commentDislikes')

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
        indexes = [
            models.Index(fields=['thread'], name='comment-idx-thread'),
            models.Index(fields=['creator'], name='comment-idx-creator'),
            models.Index(fields=['thread', 'creator'], name='comment-idx-thread-creator'),
        ]
        verbose_name_plural = 'Comment'
