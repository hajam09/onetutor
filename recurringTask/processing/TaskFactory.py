from recurringTask.processing.TaskComponent import TaskComponent
from recurringTask.processing.TaskExecutionContext import TaskExecutionContext


class TaskFactory(TaskComponent):

    def __init__(self):
        self.context = TaskExecutionContext()

        self.execute(self.context)
        self.complete()

    def execute(self, context: TaskExecutionContext):
        # sub class should contain the task instructions
        pass

    def afterComplete(self):
        if self.context.progress is None:
            self.context.createTaskProgress(1)
        self.context.progress.addProgress(1)
