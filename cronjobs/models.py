from django.db import models

from tutoring.models import Component


class TaskDefinition(models.Model):
    internalKey = models.CharField(max_length=1024)
    frequency = models.ForeignKey(Component, null=True, on_delete=models.SET_NULL, limit_choices_to={'componentGroup__code': 'TASK_FREQUENCY'})
    reference = models.CharField(max_length=2048)
    deleteFl = models.BooleanField(default=False)
    orderNo = models.IntegerField(default=1, blank=True, null=True)
    versionNo = models.IntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return self.internalKey
