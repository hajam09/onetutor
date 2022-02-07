from django.http import Http404
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


def backlog(request, internalKey):
    return render(request, 'jira2/backLog.html')


def projects(request):
    """
    TODO: Filter dropdown to filter projects by name, name contains, lead, status (show ongoing and terminated)...
    """
    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(isPrivate=False)).distinct()
    developerProfiles = DeveloperProfile.objects.all()


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

        newMembers = [i for i in developerProfiles if str(i.user.pk) in request.POST.getlist('project-project')]
        newProject.members.add(*newMembers)
        newProject.members.add(request.user)

    context = {
        'projects': allProjects,
        'developerProfiles': developerProfiles
    }
    return render(request, 'jira2/projects.html', context)


def project(request, url):
    return render(request, "jira2/project.html")


def boards(request):
    """
    TODO: Allow user to copy board on template and make changes before creating new board.
    TODO: On Admin column, display dev profile icons.
    TODO: On Project column, display project icon.
    """

    allBoards = (Board.objects.filter(isPrivate=True, admins__in=[request.user]) | Board.objects.filter(isPrivate=True, members__in=[request.user]) | Board.objects.filter(isPrivate=False)).distinct()
    developerProfiles = DeveloperProfile.objects.all()
    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(isPrivate=False)).distinct()

    if request.method == "POST":

        boardAdmins = [ i.user for i in developerProfiles if str(i.user.pk) in request.POST.getlist('board-admins') ]
        boardMembers = [ i.user for i in developerProfiles if str(i.user.pk) in request.POST.getlist('board-members') ]
        boardProjects = [ i for i in allProjects if str(i.pk) in request.POST.getlist('board-projects') ]

        newBoard = Board.objects.create(
            name=request.POST['board-name'],
            isPrivate=request.POST['board-visibility'] == 'visibility-members'
        )

        newBoard.projects.add(*boardProjects)
        newBoard.members.add(*boardMembers)
        newBoard.admins.add(*boardAdmins)

    context = {
        'projects': allProjects,
        'boards': allBoards,
        'developerProfiles': developerProfiles
    }
    return render(request, 'jira2/boards.html', context)


def board(request, url):
    return render(request, "jira2/board.html")


def boardSettings(request, url):

    try:
        thisBoard = Board.objects.get(url=url)
    except Board.DoesNotExist:
        raise Http404

    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(isPrivate=False)).distinct()
    developerProfiles = DeveloperProfile.objects.all()

    if request.is_ajax():
        boardName = request.GET.get('board-name', None)

        addProject = request.GET.get('add-project', None)
        removeProject = request.GET.get('remove-project', None)

        addAdmin = request.GET.get('add-admin', None)
        removeAdmin = request.GET.get('remove-admin', None)

        addMember = request.GET.get('add-member', None)
        removeMember = request.GET.get('remove-member', None)

        if boardName is not None:
            thisBoard.name = boardName

        if addProject is not None:
            for _project in allProjects:
                if str(_project.id) == addProject:
                    thisBoard.projects.add(_project)

        if removeProject is not None:
            for _project in thisBoard.projects.all():
                if str(_project.id) == removeProject:
                    thisBoard.projects.remove(_project)
                    break

        if addAdmin is not None:
            for _admin in developerProfiles:
                if str(_admin.user.id) == addAdmin:
                    thisBoard.admins.add(_admin.user)
                    break

        if removeAdmin is not None:
            for _admin in thisBoard.admins.all():
                if str(_admin.id) == removeAdmin:
                    thisBoard.admins.remove(_admin)
                    break

        if addMember is not None:
            for _member in developerProfiles:
                if str(_member.user.id) == addMember:
                    thisBoard.members.add(_member.user)
                    break

        if removeMember is not None:
            for _member in thisBoard.members.all():
                if str(_member.id) == removeMember:
                    thisBoard.members.remove(_member)
                    break

        thisBoard.save()


    context = {
        'board': thisBoard,
        'projects': allProjects,
        'developerProfiles': developerProfiles
    }

    return render(request, 'jira2/boardSettings.html', context)


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
    return render(request, 'jira2/ticketPage.html')


def kanbanBoard(request, internalKey):
    return render(request, "jira2/kanbanBoard.html")
