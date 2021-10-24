from enum import Enum


class BaseEnum(Enum):

    @classmethod
    def list(cls, sortByName):
        dropDowns = list(map(lambda c: "<option>" + c.value + "</option>", cls))
        if sortByName:
            dropDowns.sort()
        return "".join(dropDowns)

    def __str__(self):
        return self.value


class Project(BaseEnum):
    ONE_TUTOR = "OneTutor (OT)"
    DASHBOARD = "Dashboard"
    JIRA = "Jira"


class IssueType(BaseEnum):
    BUG = "Bug"
    IMPROVEMENT = "Improvement"
    STORY = "Story"
    TASK = "Task"
    TEST = "Test"
    EPIC = "Epic"


class Priority(BaseEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    NONE = "None"


class Status(BaseEnum):
    OPEN = "Open"
    PROGRESS = "Progress"
    DONE = "Done"
    CANCELLED = "Cancelled"
    NONE = "None"
