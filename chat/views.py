from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from accounts.models import TutorProfile, StudentProfile
from chat.models import Thread


@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread', 'first_person__tutorProfile', 'second_person__tutorProfile', 'first_person__studentProfile', 'second_person__studentProfile').order_by('timestamp')
    try:
        profile = TutorProfile.objects.get(user=request.user)
    except TutorProfile.DoesNotExist:
        profile = None

    if profile is None:
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            profile = None
    context = {
        'Threads': threads,
        'profile': profile,
    }
    return render(request, 'messages.html', context)
