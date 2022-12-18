import operator
import os
import random
import string
from functools import reduce

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from accounts.models import Education
from accounts.models import ParentProfile
# from accounts.models import SocialConnection
from accounts.models import StudentProfile
from accounts.models import TutorProfile


def tutorProfileExists(user: User):
    return TutorProfile.objects.filter(user=user).exists()


def studentProfileExists(user: User):
    return StudentProfile.objects.filter(user=user).exists()


def parentProfileExists(user: User):
    return ParentProfile.objects.filter(user=user).exists()


def userHasProfile(user: User):
    return tutorProfileExists(user) or studentProfileExists(user) or parentProfileExists(user)


def getTutorProfileForUser(user: User):
    try:
        profile = user.tutorProfile
    except TutorProfile.DoesNotExist:
        profile = None

    return profile


def getStudentProfileForUser(user: User):
    try:
        profile = user.studentProfile
    except StudentProfile.DoesNotExist:
        profile = None

    return profile


def getParentProfileForUser(user: User):
    try:
        profile = user.parentProfile
    except ParentProfile.DoesNotExist:
        profile = None

    return profile


def getProfileForUser(user: User):
    tutorProfile = getTutorProfileForUser(user)
    studentProfile = getStudentProfileForUser(user)
    parentProfile = getParentProfileForUser(user)

    return tutorProfile or studentProfile or parentProfile


def isPasswordStrong(password):
    if len(password) < 8:
        return False

    if not any(letter.isalpha() for letter in password):
        return False

    if not any(capital.isupper() for capital in password):
        return False

    if not any(number.isdigit() for number in password):
        return False

    return True


def getTutorRequestedStoredData(request, user: User):
    userData = {
        "user": {
            "firstName": request.user.first_name,
            "lastName": request.user.last_name,
            "email": request.user.email,
            "username": request.user.username,
            "status": "Active" if request.user.is_active else "In-Active"
        },
        "education": [
            {
                "schoolName": e.schoolName,
                "qualification": e.qualification,
                "startDate": str(e.startDate),
                "endDate": str(e.endDate)
            }
            for e in Education.objects.filter(user=request.user)
        ],
        "availability": user.availability.getAvailability(),
        "lessons": [
            {
                "tutor": l.tutor.user.get_full_name(),
                "student": "Redacted",
                "hoursTaught": getHoursTaught(l.hoursTaught),
                "dateTime": str(l.dateTime.strftime("%d/%m/%Y %H:%M:%S")),
                "points": l.points,
                "amount": "£" + str(l.amount),

            }
            for l in user.tutorProfile.tutorLessons.all()
        ],
        # "socialConnections": [
        #     {
        #         "twitterUrl": s.twitter,
        #         "facebookUrl": s.facebook,
        #         "googleUrl": s.google,
        #         "linkedinUrl": s.linkedin,
        #     }
        #     for s in SocialConnection.objects.filter(user=user)
        # ]
    }
    return userData


def getHoursTaught(time):
    hours = int(time)
    minutes = (time * 60) % 60
    return "%d:%02d" % (hours, minutes)


def getClientInternetProtocolAddress(request):
    forwardedFor = request.META.get('HTTP_X_FORWARDED_FOR')

    if forwardedFor:
        ip = forwardedFor.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def removeProfilePictureFromServer(profile):
    if profile.picture and "profile-picture/default-img/" not in profile.picture.url:
        previousProfileImage = os.path.join(settings.MEDIA_ROOT, profile.picture.name)
        if os.path.exists(previousProfileImage):
            os.remove(previousProfileImage)


def generateRandomString(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def convertRatingToStars(value):
    pureRating = int(value)
    decimalPart = value - pureRating
    finalScore = "+" * pureRating

    if decimalPart >= 0.75:
        finalScore += "+"
    elif decimalPart >= 0.25:
        finalScore += "_"
    return finalScore.replace('+', '<i class="far fa-star"></i>').replace('_', '<i class="fas fa-star-half"></i>')


def performComplexTutorSearch(request, filterList=None):
    filterList = filterList or []

    filterList.append(reduce(operator.or_, [Q(**{"createdDateTime__isnull": False})]))

    if request.GET.get("subject") is not None:
        filterList.append(
            reduce(
                operator.or_,
                [Q(**{f'subjects__icontains': subject}) for subject in request.GET.get("subject").split(" ")]
            )
        )

    return TutorProfile.objects.filter(reduce(operator.and_, filterList))


def userSerializer(user):
    return {
        "firstName": user.first_name,
        "lastName": user.last_name,
    }


class Tab:

    def __init__(self, profile, tab, internalKey, identifier, icon):
        self.profile = profile
        self.tab = tab
        self.internalKey = internalKey
        self.identifier = identifier
        self.url = reverse("accounts:settings-view") + f"?profile={profile}&tab={tab}"
        self.icon = icon


def getTutorSettingsTab():
    return [
        Tab("tutor", "general", "General", "id-nav-tab-general", "fas fa-user mr-2"),
        Tab("tutor", "biography", "Biography", "id-nav-tab-biography", "fa fa-book mr-2"),
        Tab("tutor", "security", "Security", "id-nav-tab-security", "fas fa-key mr-2"),
        Tab("tutor", "notification", "Notification", "id-nav-tab-notification", "fas fa-bell-slash mr-2"),
        Tab("tutor", "account", "Account", "id-nav-tab-account", "fas fa-trash-alt mr-2"),
    ]


def getStudentSettingsTab():
    return [
        Tab("student", "general", "General", "id-nav-tab-general", "fas fa-user mr-2"),
        Tab("student", "biography", "Biography", "id-nav-tab-biography", "fa fa-book mr-2"),
        Tab("student", "security", "Security", "id-nav-tab-security", "fas fa-key mr-2"),
        Tab("student", "notification", "Notification", "id-nav-tab-notification", "fas fa-bell-slash mr-2"),
        Tab("student", "account", "Account", "id-nav-tab-account", "fas fa-trash-alt mr-2"),
    ]


def getParentSettingsTab():
    return [
        Tab("parent", "general", "General", "id-nav-tab-general", "fas fa-user mr-2"),
        Tab("parent", "my-children", "My Children", "id-nav-tab-children", "fa fa-book mr-2"),
        Tab("parent", "security", "Security", "id-nav-tab-security", "fas fa-key mr-2"),
        Tab("parent", "notification", "Notification", "id-nav-tab-notification", "fas fa-bell-slash mr-2"),
        Tab("parent", "account", "Account", "id-nav-tab-account", "fas fa-trash-alt mr-2"),
    ]

# def performComplexQuizSearch(query, filterList=None):
#     filterList = filterList or []
#     attributesToSearch = [
#         'name', 'description', 'url',
#         'topic__name', 'topic__description',
#         'topic__subject__name', 'topic__subject__description'
#     ]
#
#     filterList.append(reduce(operator.or_, [Q(**{'deleteFl': False})]))
#     if query and query.strip():
#         filterList.append(reduce(operator.or_, [Q(**{f'{v}__icontains': query}) for v in attributesToSearch]))
#
#     return Quiz.objects.filter(reduce(operator.and_, filterList)).select_related('topic__subject').distinct()
