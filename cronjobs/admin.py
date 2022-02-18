from django.contrib import admin

from cronjobs.models import TaskDefinition

admin.site.register(TaskDefinition)
