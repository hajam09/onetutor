from django.shortcuts import render


def indexView(request):
    return render(request, 'forum/indexView.html')


def postView(request):
    return render(request, 'forum/postView.html')
