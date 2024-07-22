from django.shortcuts import render


def indexView(request):
    return render(request, 'core/indexView.html')
