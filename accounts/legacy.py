import operator
import os
from functools import reduce

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render

from accounts.models import TutorProfile, StudentProfile
from onetutor import settings
from onetutor.decorators.deprecated import deprecated
from onetutor.operations import databaseOperations, generalOperations, tutorOperations
from tutoring.models import Component, Availability, ComponentGroup


@login_required
@deprecated
def userSettings(request):
    # TODO: Find a good code design for the below try/catch.
    # TODO: Split page and view with student/tutor and each tabs within each profile for reusability.
    try:
        profile = TutorProfile.objects.select_related('user', 'user__availability').prefetch_related(
            'teachingLevels').get(user=request.user)
    except TutorProfile.DoesNotExist:
        profile = None

    if profile is None:
        try:
            profile = StudentProfile.objects.select_related('user').get(user=request.user)
        except StudentProfile.DoesNotExist:
            profile = None

    if profile is None:
        return redirect('accounts:select-profile')

    if isinstance(profile, TutorProfile):
        # functions specific to tutors.
        templateName = "accounts/tutorSettings.html"

        educationLevelComponents = Component.objects.filter(componentGroup__code="EDUCATION_LEVEL")
        educationLevelComponent = [i for i in educationLevelComponents if i not in profile.teachingLevels.all()]

        if request.method == "POST" and "updateTutorProfile" in request.POST:
            summary = request.POST["summary"]
            about = request.POST["about"]
            subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])
            availabilityChoices = request.POST.getlist('availabilityChoices')
            teachingLevels = request.POST.getlist('teachingLevels')

            request.user.availability.delete()
            availability = Availability.objects.create(user=request.user)
            for i in availabilityChoices:
                setattr(availability, i, True)
            availability.save()

            profile.summary = summary
            profile.about = about
            profile.subjects = subjects
            profile.save()

            messages.success(
                request,
                'Your biography and other details has been updated successfully.'
            )
            profile.teachingLevels.clear()
            profile.teachingLevels.add(*[i for i in educationLevelComponents if i.internalKey in teachingLevels])

    else:
        # functions specific to students .
        templateName = "accounts/studentSettings.html"

        educationLevelComponent = []

        if request.method == "POST" and "updateStudentProfile" in request.POST:
            about = request.POST["about"]
            subjects = ', '.join([i.capitalize() for i in request.POST.getlist('subjects')])

            profile.about = about
            profile.subjects = subjects
            profile.save()

            messages.success(
                request,
                'Your biography and other details has been updated successfully.'
            )

    if request.method == "POST" and "updateEducation" in request.POST:
        schoolNames = request.POST.getlist('schoolName')
        qualifications = request.POST.getlist('qualification')
        startDates = request.POST.getlist('startDate')
        endDates = request.POST.getlist('endDate')

        databaseOperations.createEducationInBulk(request, schoolNames, qualifications, startDates, endDates)

    if request.method == "POST" and "updateGeneralInformation" in request.POST:
        firstname = request.POST["firstName"].strip()
        lastname = request.POST["lastName"].strip()

        if "profilePicture" in request.FILES:
            if profile.profilePicture and 'profilepicture/defaultimg/' not in profile.profilePicture.url:
                previousProfileImage = os.path.join(settings.MEDIA_ROOT, profile.profilePicture.name)
                if os.path.exists(previousProfileImage):
                    os.remove(previousProfileImage)

            profile.profilePicture = request.FILES["profilePicture"]
            profile.save(update_fields=['profilePicture'])

        user = request.user
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        messages.success(
            request,
            'Your personal details has been updated successfully.'
        )

    if request.method == "POST" and "changePassword" in request.POST:
        currentPassword = request.POST["currentPassword"]
        newPassword = request.POST["newPassword"]
        confirmPassword = request.POST["confirmPassword"]

        user = request.user

        if currentPassword and not user.check_password(currentPassword):
            messages.error(
                request,
                'Your current password does not match with the account\'s existing password.'
            )

        if newPassword and confirmPassword:
            if newPassword != confirmPassword:
                messages.error(
                    request,
                    'Your new password and confirm password does not match.'
                )

            if not generalOperations.isPasswordStrong(newPassword):
                messages.warning(
                    request,
                    'Your new password is not strong enough.'
                )

            user.set_password(newPassword)
        user.save()

        if newPassword and confirmPassword:
            user = authenticate(username=user.username, password=newPassword)
            if user:
                messages.success(
                    request,
                    'Your password has been updated.'
                )
            # signIn(request, user)
            else:
                messages.warning(
                    request,
                    'Something happened. Try to login to the system.'
                )
                return redirect("accounts:login")

    if request.method == "POST" and "notificationSettings" in request.POST:
        loginAttemptNotification = True if request.POST.get('loginAttemptNotification') else False
        questionAnswerNotification = True if request.POST.get('questionAnswerNotification') else False
        answerOnForum = True if request.POST.get('answerOnForum') else False
        messageOnChat = True if request.POST.get('messageOnChat') else False
    # TODO: Need to create a Notifications table for each user and add it to event listener.

    if request.method == "POST" and "deleteAccount" in request.POST:
        if request.POST["delete-code"] == request.session.session_key:
            request.user.delete()
            messages.success(
                request,
                'Account deleted successfully'
            )
            return redirect('tutoring:mainpage')
        messages.error(
            request,
            'Account delete code is incorrect, please try again later.'
        )

    context = {
        "profile": profile,
        "educationLevelComponent": educationLevelComponent
    }
    return render(request, templateName, context)


# url(r'^tutors/(?P<searchParameters>.*)/$', views.searchBySubjectAndFilter, name='searchBySubjectAndFilter'),
@deprecated
def searchBySubjectAndFilter(request, searchParameters=""):
    if request.method == "POST" and request.POST["generalQuery"]:
        return redirect("tutoring:searchBySubjectAndFilter", searchParameters=request.POST["generalQuery"])

    searchParametersSplit = searchParameters.split("/")
    subject = searchParametersSplit[0].lower().split(" ")

    try:
        filters = searchParametersSplit[1]
    except IndexError:
        filters = None

    hourlyMinimumRate = 0
    hourlyMaximumRate = 100
    minimumScore = 0
    maximumScore = 2000
    tickedTutorFeature = []
    selectedEducationLevel = None
    selectedAverageRating = -1

    if "and" in subject:
        requiredOperator = operator.and_
        subject = list(filter("and".__ne__, subject))
    else:
        requiredOperator = operator.or_

    query = reduce(requiredOperator, (Q(subjects__icontains=s) for s in subject))
    tutorList = TutorProfile.objects.filter(query).select_related('user').prefetch_related('tutorLessons',
                                                                                           'user__tutorReviews',
                                                                                           'features', 'teachingLevels')
    if filters is not None:
        for f in filters.split("&"):
            r = f.split(":")

            if r[0] == "tutorFeature":
                tickedTutorFeature = f.split(":")[1].split(",")
                tutorList = set([t
                                 for t in tutorList
                                 for c in t.features.all()
                                 if c.code in tickedTutorFeature])

            if r[0] == "hourlyPrice":
                hourlyMinimumRate = int(f.split(":")[1].split(",")[0])
                hourlyMaximumRate = int(f.split(":")[1].split(",")[1])
                tutorList = set([
                    t for t in tutorList
                    if hourlyMinimumRate <= t.chargeRate <= hourlyMaximumRate
                ])

            if r[0] == "tutorScore":
                minimumScore = int(f.split(":")[1].split(",")[0])
                maximumScore = int(f.split(":")[1].split(",")[1])
                tutorList = set([
                    t for t in tutorList
                    if minimumScore <= sum([p.points for p in t.tutorLessons.all()]) <= maximumScore
                ])

            if r[0] == "myEducationLevel":
                selectedEducationLevel = f.split(":")[1]
                # use this to check the tutor teaching level.
                tutorList = set([
                    t for t in tutorList
                    for c in t.teachingLevels.all()
                    if c.code in selectedEducationLevel
                ])

            if r[0] == "tutorAverageRating":
                selectedAverageRating = int(f.split(":")[1])
                tutorList = set([
                    t for t in tutorList
                    if tutorOperations.getTutorsAverageRating(t) >= selectedAverageRating
                ])

    if len(tutorList) == 0:
        messages.error(
            request,
            "Sorry, we couldn't find you a tutor for your search. Try entering something broad."
        )

    # only doing this because list to queryset is not possible and queryset is needed for Paginator.
    finalResultIds = [t.id for t in tutorList]
    tutorList = TutorProfile.objects.filter(id__in=finalResultIds).select_related('user').prefetch_related(
        'tutorLessons', 'user__tutorReviews', 'features', 'teachingLevels')

    page = request.GET.get('page', 1)
    paginator = Paginator(tutorList, 15)

    try:
        tutorList = paginator.page(page)
    except PageNotAnInteger:
        tutorList = paginator.page(1)
    except EmptyPage:
        tutorList = paginator.page(paginator.num_pages)

    requiredComponentGroup = ComponentGroup.objects.filter(
        code__in=['TUTOR_FEATURE', 'EDUCATION_LEVEL', 'QUALIFICATION', 'RATING_FILTER']).prefetch_related("components")

    context = {
        "generalQuery": searchParametersSplit[0],
        "tutorList": tutorList,
        "defaultPriceValues": {"priceFrom": hourlyMinimumRate, "priceTo": hourlyMaximumRate},
        "defaultScoreValues": {"scoreFrom": minimumScore, "scoreTo": maximumScore},
        "tickedTutorFeature": tickedTutorFeature,
        "selectedEducationLevel": selectedEducationLevel,
        "selectedAverageRating": selectedAverageRating,
        "tutorFeatureGroupComponent": next(i for i in requiredComponentGroup if i.code == 'TUTOR_FEATURE'),
        "educationLevelComponent": next(i for i in requiredComponentGroup if i.code == 'EDUCATION_LEVEL'),
        "qualificationComponent": next(i for i in requiredComponentGroup if i.code == 'QUALIFICATION'),
        "ratingFilterComponent": next(i for i in requiredComponentGroup if i.code == 'RATING_FILTER'),
        "showResult": True,
    }
    return render(request, 'tutoring/mainpage.html', context)
