from django.contrib import admin
from .models import Forum, SubForum#, Comment

admin.site.register(Forum)
admin.site.register(SubForum)
# admin.site.register(Comment)