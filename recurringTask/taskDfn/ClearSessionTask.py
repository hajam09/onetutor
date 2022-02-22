from recurringTask.processing.TaskFactory import TaskFactory
from recurringTask.processing.TaskExecutionContext import TaskExecutionContext
from django.contrib.sessions.models import Session


class ClearSessionTask(TaskFactory):

    def execute(self, context: TaskExecutionContext):
        print("YOYO")
        # Session.objects.all().delete()