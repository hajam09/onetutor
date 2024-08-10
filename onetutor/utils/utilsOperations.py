from django.utils import timezone


def isBelow18(dateOfBirth):
    today = timezone.now().date()
    age = today.year - dateOfBirth.year - ((today.month, today.day) < (dateOfBirth.month, dateOfBirth.day))
    return age < 18
