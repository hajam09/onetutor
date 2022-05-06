from datetime import datetime
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render

from chat.models import Thread
from dashboard.models import UserLogin


@login_required
def chatPage(request):
    # select_related = 'firstParticipant__tutorProfile', 'firstParticipant__studentProfile', 'secondParticipant__tutorProfile', 'secondParticipant__studentProfile'
    # prefetch_related = 'threadMessages__user__tutorProfile', 'threadMessages__user__studentProfile'
    threads = Thread.objects.byUser(user=request.user).select_related('firstParticipant__tutorProfile', 'secondParticipant__tutorProfile').prefetch_related('threadMessages__user__tutorProfile').order_by('timestamp')
    onlineUsers = UserLogin.objects.filter(logoutTime__date=datetime.max.date()).select_related('user')

    if request.is_ajax():
        functionality = request.GET.get('functionality', None)

        if functionality == 'createThread':
            participantId = request.GET.get('participantId', None)
            secondParticipant = User.objects.get(id=participantId)

            # check if a thread already exists between this user and the second participant.
            if len([t for t in threads if t.firstParticipant == secondParticipant or t.secondParticipant == secondParticipant]) == 0:
                Thread.objects.create(
                    firstParticipant=request.user,
                    secondParticipant=secondParticipant
                )

        response = {
            "statusCode": HTTPStatus.OK
        }
        return JsonResponse(status=HTTPStatus.OK)

    messenger = [
        {
            'id': i.id,
            'name': getThreadName(request, i),
            'picture': getThreadPicture(request, i),
            'participantId': otherParticipantId(request, i),
            'isOnline': isUserOnline(onlineUsers, otherParticipantId(request, i)),
            'chat': [
                {
                    'date': uniqueDate,
                    'messages': [
                        {
                            'isSender': m.user == request.user,
                            'userId': m.user.pk,
                            'picture': m.getUserProfilePicture(),
                            'message': m.message,
                            'time': m.timestamp.strftime("%I:%M %p")
                        }
                        for m in getMessagesForDate(i.threadMessages.all(), uniqueDate)
                    ]
                }
                for uniqueDate in i.threadMessages.all().values_list('timestamp__date', flat=True).distinct()
            ]
        }
        for i in threads
    ]

    context = {
        'messenger': messenger,
    }
    return render(request, 'messages.html', context)


def isUserOnline(onlineUsers, participantId):
    return len([u for u in onlineUsers if u.user.id == int(participantId)]) != 0


def getMessagesForDate(messages, date):
    return [m for m in messages if m.timestamp.date() == date]


def getThreadName(request, thread):
    if thread.firstParticipant == request.user:
        return thread.secondParticipant.get_full_name()
    return thread.firstParticipant.get_full_name()


def getThreadPicture(request, thread):
    if thread.firstParticipant == request.user:
        return thread.getSecondPersonProfilePicture()
    return thread.getFirstPersonProfilePicture()


def otherParticipantId(request, thread):
    if thread.firstParticipant == request.user:
        return thread.secondParticipant.id
    return thread.firstParticipant.id
