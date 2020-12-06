from django.contrib import admin
from .models import Category, Community, Forum, Comment

admin.site.register(Category)
admin.site.register(Community)
admin.site.register(Forum)
admin.site.register(Comment)