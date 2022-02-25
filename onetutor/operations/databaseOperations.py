from accounts.models import Education


def getObjectById(objects, pk):
    return next((o for o in objects if o.id == int(pk)), None)


def createEducationInBulk(request, schoolNames, qualifications, startDates, endDates):
    if len(schoolNames) != len(qualifications) != len(startDates) != len(endDates):
        return

    # Delete all previous education for this user and create new object(s).
    request.user.education.all().delete()
    Education.objects.bulk_create(
        [
            Education(
                user=request.user,
                schoolName=schoolName,
                qualification=qualification,
                startDate=startDate,
                endDate=endDate
            )
            for schoolName, qualification, startDate, endDate in zip(schoolNames, qualifications, startDates, endDates)
        ]
    )
