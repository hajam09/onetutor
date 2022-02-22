from abc import (
    ABC,
    abstractmethod
)

from recurringTask.processing.TaskExecutionContext import TaskExecutionContext


class TaskComponent(ABC):

    def restart(self, context: TaskExecutionContext):
        pass

    @abstractmethod
    def execute(self, context: TaskExecutionContext):
        # sub class should contain the task instructions
        pass

    def complete(self):
        pass

    def cancelled(self):
        pass

    def fail(self):
        pass

    def afterComplete(self):
        pass

    def createChildTask(self):
        pass
