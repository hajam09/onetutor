from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Community(models.Model):
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	community_title = models.TextField()
	community_url = models.CharField(max_length=512)
	community_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField()
	community_likes = models.ManyToManyField(User, related_name='community_likes')
	community_dislikes = models.ManyToManyField(User, related_name='community_dislikes')

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

# class Comment(models.Model):
# 	forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
# 	creator = models.ForeignKey(User, on_delete=models.CASCADE)
# 	forum_description = models.TextField(max_length=1024)
# 	created_at = models.DateTimeField(default=datetime.now)
# 	anonymous = models.BooleanField()
# 	comment_likes = models.ManyToManyField(User, related_name='comment_likes')
# 	comment_dislikes = models.ManyToManyField(User, related_name='comment_dislikes')