from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from chat.models import Thread
from onetutor.operations import generalOperations


def getThreadName(request, thread):
    if thread.first_person == request.user:
        return thread.second_person.get_full_name()
    else:
        return thread.first_person.get_full_name()


def getThreadPicture(request, thread):
    if thread.first_person == request.user:
        return thread.getSecondPersonProfilePicture()
    else:
        return thread.getFirstPersonProfilePicture()


def otherParticipantId(request, thread):
    if thread.first_person == request.user:
        return thread.second_person.id
    else:
        return thread.first_person.id


@login_required
def messages_page(request):
    # select_related = 'first_person__tutorProfile', 'first_person__studentProfile', 'second_person__tutorProfile', 'second_person__studentProfile'
    # prefetch_related = 'threadMessages__user__tutorProfile', 'threadMessages__user__studentProfile'
    threads = Thread.objects.by_user(user=request.user).select_related('first_person__tutorProfile','second_person__tutorProfile').prefetch_related('threadMessages__user__tutorProfile').order_by('timestamp')

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
