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


class Forum(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    url = models.CharField(max_length=8, default=generateRandomString)
    description = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='forumLikes')
    dislikes = models.ManyToManyField(User, related_name='forumDislikes')
    picture = models.ImageField(blank=True, null=True, upload_to='forum-image/')
    watchers = models.ManyToManyField(User, related_name='forumWatchers')

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
            models.Index(fields=['creator'], name='forum-idx-creator'),
            models.Index(fields=['title'], name='forum-idx-title'),
            models.Index(fields=['description'], name='forum-idx-description'),
        ]
        verbose_name_plural = 'Forum'


class ForumComment(BaseModel):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='forumComments')
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name='forumCommentLikes')
    dislikes = models.ManyToManyField(User, related_name='forumCommentDislikes')

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
            models.Index(fields=['forum'], name='forum-comment-idx-forum'),
            models.Index(fields=['creator'], name='forum-comment-idx-creator'),
            models.Index(fields=['forum', 'creator'], name='forum-comment-idx-book-creator'),
        ]
        verbose_name_plural = 'ForumComment'
