from django.contrib.auth.models import User

from recurringTask.processing.TaskExecutionContext import TaskExecutionContext
from recurringTask.processing.TaskFactory import TaskFactory


class LastLoginUsersNotification(TaskFactory):

    def execute(self, context: TaskExecutionContext):
        allUsers = User.objects.all()
        progress = context.createTaskProgress(allUsers.count())

        # for user in allUsers:
        #     progress.addProgress(1)