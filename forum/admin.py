from django.contrib import admin

from forum.models import (
    Category,
    Thread,
    Comment
)

admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Comment)
