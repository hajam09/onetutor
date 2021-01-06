from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Category(models.Model):
	name = models.CharField(max_length=512)

	class Meta:
		verbose_name_plural = "Categories"
		ordering = ('name',)

	def __str__(self):
		return self.name

class Community(models.Model):
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.ForeignKey(Category, models.SET_NULL, null=True)
	community_title = models.TextField()
	community_url = models.CharField(max_length=512)
	community_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	community_likes = models.ManyToManyField(User, related_name='community_likes')
	community_dislikes = models.ManyToManyField(User, related_name='community_dislikes')
	community_banner = models.ImageField(upload_to='communitybanner/', blank=True, null=True)

	class Meta:
		verbose_name_plural = "Communities"

class Forum(models.Model):
	community = models.ForeignKey(Community, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forum_title = models.TextField()
	forum_url = models.CharField(max_length=512)
	forum_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField(default=False)
	forum_likes = models.ManyToManyField(User, related_name='forum_likes')
	forum_dislikes = models.ManyToManyField(User, related_name='forum_dislikes')
	forum_image = models.ImageField(upload_to='forumimage/', blank=True, null=True)

	class Meta:
		verbose_name_plural = "Forums"

class ForumComment(models.Model):
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	comment_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField(default=False)
	reply = models.ForeignKey('ForumComment', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
	forum_comment_likes = models.ManyToManyField(User, related_name='forum_comment_likes')
	forum_comment_dislikes = models.ManyToManyField(User, related_name='forum_comment_dislikes')

	class Meta:
		verbose_name_plural = "ForumComment"