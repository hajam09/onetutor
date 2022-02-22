from recurringTask.processing.BaseTaskProgress import BaseTaskProgress


class TaskExecutionContext:

    def __init__(self):
        self.taskArguments = {}  # NEVER AMEND taskArguments DIRECTLY
        self.progress = None

    def createTaskProgress(self, total):
        self.progress = BaseTaskProgress(total)
        return self.progress

    def addTaskArgument(self, key, value):
        self.taskArguments[key] = value

    def removeTaskArgument(self, key):
        if key in self.taskArguments:
            self.taskArguments.pop(key)
