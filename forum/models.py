from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Category(models.Model):
	name = models.CharField(max_length=512)
	# Once created, it should not be deleted.

	class Meta:
		verbose_name_plural = "Categories"
		ordering = ('name',)

	def __str__(self):
		return self.name

class Community(models.Model):
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
	community_title = models.TextField()
	community_url = models.CharField(max_length=512)
	community_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField()#deprecate it
	community_likes = models.ManyToManyField(User, related_name='community_likes')
	community_dislikes = models.ManyToManyField(User, related_name='community_dislikes')

	class Meta:
		verbose_name_plural = "Communities"

class Forum(models.Model):
	community = models.ForeignKey(Community, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forum_title = models.TextField()
	forum_url = models.CharField(max_length=512)
	forum_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField()
	forum_likes = models.ManyToManyField(User, related_name='forum_likes')
	forum_dislikes = models.ManyToManyField(User, related_name='forum_dislikes')

	class Meta:
		verbose_name_plural = "Forums"

class Comment(models.Model):
	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forum_description = models.TextField(max_length=1024)
	created_at = models.DateTimeField(default=datetime.now)
	reply = models.ForeignKey('Comment', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
	comment_likes = models.ManyToManyField(User, related_name='comment_likes')
	comment_dislikes = models.ManyToManyField(User, related_name='comment_dislikes')

	class Meta:
		verbose_name_plural = "Comments"