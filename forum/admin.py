from django.contrib import admin

from forum.models import (
    Category,
    Forum,
    ForumComment
)

admin.site.register(Category)
admin.site.register(Forum)
admin.site.register(ForumComment)
