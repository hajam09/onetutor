from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Forum(models.Model):
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forum_title = models.TextField()
	forum_url = models.CharField(max_length=512)
	forum_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField()
	forum_likes = models.ManyToManyField(User, related_name='forum_likes')
	forum_dislikes = models.ManyToManyField(User, related_name='forum_dislikes')

class SubForum(models.Model):
	parent_forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
	forum_title = models.TextField()
	forum_url = models.CharField(max_length=512)
	forum_description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	anonymous = models.BooleanField()
	sub_forum_likes = models.ManyToManyField(User, related_name='sub_forum_likes')
	sub_forum_dislikes = models.ManyToManyField(User, related_name='sub_forum_dislikes')

# class Comment(models.Model):
# 	sub_forum = models.ForeignKey(SubForum, on_delete=models.CASCADE)
# 	creator = models.ForeignKey(User, on_delete=models.CASCADE)
# 	forum_description = models.TextField(max_length=1024)
# 	created_at = models.DateTimeField(default=datetime.now)
# 	anonymous = models.BooleanField()
# 	comment_likes = models.ManyToManyField(User, related_name='comment_likes')
# 	comment_dislikes = models.ManyToManyField(User, related_name='comment_dislikes')