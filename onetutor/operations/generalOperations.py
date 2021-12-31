from django.contrib.auth.models import User

from accounts.models import Education
from accounts.models import SocialConnection


def isPasswordStrong(password):
    if len(password) < 8:
        return False

    if not any(letter.isalpha() for letter in password):
        return False

    if any(capital.isupper() for capital in password):
        return False

    if any(number.isdigit() for number in password):
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
        "socialConnections": [
            {
                "twitterUrl": s.twitter,
                "facebookUrl": s.facebook,
                "googleUrl": s.google,
                "linkedinUrl": s.linkedin,
            }
            for s in SocialConnection.objects.filter(user=user)
        ]
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