from django.shortcuts import render

from jira2.models import *


# def mainPage(request):
#     """
#     for the authenticated user get the board,
#     if board == null then the user is not on the company.
#     else:
#         get the sprint for that board.
#         if the sprint is currently running then return to the sprint board page.
#         else:
#         return to the backlog for now.
#     """
#
#     try:
#         board = BoardA.objects.get(members__in=[request.user])
#     except ObjectDoesNotExist:
#         raise RuntimeWarning('this user is not part of any board.')
#     except MultipleObjectsReturned:
#         raise RuntimeWarning('this user is part of more than one board. this user should be in one board only.')
#
#     sprint = board.sprint
#
#     if sprint.startDate <= datetime.date.today() <= sprint.endDate:
#         return redirect('jira2:sprintBoard')
#
#     return redirect('jira:backlog')  # return redirect('jira2:sprintBoard')
#
#
# def sprintBoard(request):
#     """
#     for this user, get the board and check if only one board is returned else raise exception.
#     check if a sprint is active, else place a button to activate the sprint.
#     when new sprint is activated. get the previous sprint.
#     get the completed tickets and set it to deleteFl = true.
#     """
#     try:
#         board = BoardA.objects.get(members__in=[request.user])
#     except ObjectDoesNotExist:
#         raise RuntimeWarning('this user is not part of any board.')
#     except MultipleObjectsReturned:
#         board = BoardA.objects.filter(members__in=[request.user]).first()
#
#     sprint = board.sprint
#
#     _board = {
#         'boardName': board.internalKey,
#         'columns': [
#             {
#                 'id': i.pk,
#                 'name': i.internalKey.upper(),
#                 'tickets': [
#                     {
#                         'id': j.id,
#                         'internalKey': j.internalKey,
#                         'summary': j.summary,
#                         'points': j.points,
#                         'issueType': {
#                             'internalKey': j.issueType.internalKey,
#                             'code': j.issueType.code,
#                             'icon': j.issueType.icon,
#                         },
#                         'priority': {
#                             'internalKey': j.priority.internalKey,
#                             'icon': j.priority.icon,
#                         }
#                     }
#                     for j in i.columnTickets.all()
#                 ],
#             }
#             for i in board.boardColumns.all()
#         ]
#     }
#
#     context = {
#         'isSprintActive': sprint.startDate <= datetime.date.today() <= sprint.endDate,
#         'board': _board,
#     }
#     return render(request, "jira2/sprintBoard.html", context)


def dashboard(request):
    return render(request, "jira2/dashboard.html")


def backlog(request):
    return render(request, "jira2/backLog.html")


def projects(request):
    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(isPrivate=False)).distinct()
    members = User.objects.all()[:30]


    if request.method == "POST":
        newProject = Project.objects.create(
            name=request.POST['project-name'],
            code=request.POST['project-code'],
            lead=request.user,
            status=Component.objects.get(componentGroup__internalKey='Project Status', code='ON_GOING'),
            startDate=request.POST['project-start'] or datetime.date.today(),
            endDate=request.POST['project-due'] or datetime.datetime.max,
            isPrivate=request.POST['project-visibility'] == 'visibility-members',
            description=request.POST['project-description'],
            icon=request.FILES.get('project-icon', None),
        )

        newMembers = User.objects.filter(id__in=request.POST.getlist('project-users'))
        newProject.members.add(*newMembers)

    context = {
        'projects': allProjects,
        'members': members
    }
    return render(request, 'jira2/projects.html', context)


def project(request, url):
    return render(request, "jira2/project.html")


def boards(request):
    return render(request, "jira2/boards.html")


def board(request, url):
    return render(request, "jira2/board.html")


def yourWork(request):
    return render(request, "jira2/yourWork.html")


def teams(request):
    return render(request, "jira2/teams.html")


def team(request, internalKey):
    return render(request, "jira2/team.html")


def searchPeople(request):
    return render(request, "jira2/searchPeople.html")


def profile(request):
    return render(request, "jira2/profile.html")


def ticketPage(request, internalKey):
    context = {
        'project': {
            'id': 1,
            'name': 'Thor'
        },
        'ticket': {
            'id': 1,
            'key': internalKey,
            'issueType': 'Epic',
            'issueIcon': '',
            'summary': 'Contract Entity',
            'description': 'This new feature will add the ability for commercial pricing...',
            'userImpact': '',
            'technicalImpact': '',
            'releaseImpact': '',
            'automatedTestingReason': '',
        }
    }

    return render(request, "jira2/ticketPage.html", context)


def kanbanBoard(request, internalKey):
    return render(request, "jira2/kanbanBoard.html")
