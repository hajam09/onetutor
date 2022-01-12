from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.models import Thread


@login_required
def chatPage(request):
    # select_related = 'firstParticipant__tutorProfile', 'firstParticipant__studentProfile', 'secondParticipant__tutorProfile', 'secondParticipant__studentProfile'
    # prefetch_related = 'threadMessages__user__tutorProfile', 'threadMessages__user__studentProfile'
    threads = Thread.objects.byUser(user=request.user).select_related('firstParticipant__tutorProfile','secondParticipant__tutorProfile').prefetch_related('threadMessages__user__tutorProfile').order_by('timestamp')

    messenger = [
        {
            'id': i.id,
            'name': getThreadName(request, i),
            'picture': getThreadPicture(request, i),
            'participantId': otherParticipantId(request, i),
            'messages': [
                {
                    'isSender': j.user == request.user,
                    'userId': j.user.pk,
                    'picture': j.getUserProfilePicture(),
                    'message': j.message,
                }
                for j in i.threadMessages.all()
            ]
        }
        for i in threads
    ]

    context = {
        'messenger': messenger,
    }
    return render(request, 'messages.html', context)


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
