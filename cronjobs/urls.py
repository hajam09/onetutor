from pydoc import locate

from background_task import background

from cronjobs.models import TaskDefinition

app_name = "cronjobs"

urlpatterns = [
]

tasks = TaskDefinition.objects.all()


def importClass(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def runTask(task):
    clazz = locate(task.reference)
    if clazz is not None:
        getattr(clazz, task.reference.split('.')[-1])()


@background(schedule=1)
def recurringEverySecond():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_SECOND']


@background(schedule=60)
def recurringEveryMinute():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_MINUTE']


@background(schedule=3600)
def recurringEveryHour():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_HOUR']


@background(schedule=86400)
def recurringEveryDay():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_DAY']


@background(schedule=86400 * 5)
def recurringFiveDays():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_FIVE_DAYS']


@background(schedule=86400 * 10)
def recurringTenDays():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_TEN_DAYS']


@background(schedule=86400 * 15)
def recurringFifteenDays():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_FIFTEEN_DAYS']


@background(schedule=86400 * 20)
def recurringTwentyDays():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_TWENTY_DAYS']


@background(schedule=86400 * 25)
def recurringTwentyFiveDays():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_TWENTY_FIVE_DAYS']


@background(schedule=86400 * 30)
def recurringEveryMonth():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_MONTH']


@background(schedule=86400 * 182)
def recurringEverySixMonths():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_SIX_MONTHS']


@background(schedule=86400 * 365)
def recurringEveryYear():
    [runTask(i) for i in tasks if i.frequency.code == 'EVERY_YEAR']


recurringEverySecond()
recurringEveryMinute()
recurringEveryHour()
recurringEveryDay()
recurringFiveDays()
recurringTenDays()
recurringFifteenDays()
recurringTwentyDays()
recurringTwentyFiveDays()
recurringEveryMonth()
recurringEverySixMonths()
recurringEveryYear()
