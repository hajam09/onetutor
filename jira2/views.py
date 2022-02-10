from http import HTTPStatus

from django.http import Http404, JsonResponse
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
    """

    privateAdminBoards = Board.objects.filter(isPrivate=True, admins__in=[request.user]).prefetch_related('projects', 'admins__developerProfile')
    privateMemberBoards = Board.objects.filter(isPrivate=True, members__in=[request.user]).prefetch_related('projects', 'admins__developerProfile')
    nonPrivateBoards = Board.objects.filter(isPrivate=False).prefetch_related('projects', 'admins__developerProfile')

    allBoards = (privateAdminBoards | privateMemberBoards | nonPrivateBoards).distinct()
    developerProfiles = DeveloperProfile.objects.all().select_related('user')
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
        thisBoard = Board.objects.prefetch_related('boardColumns', 'boardLabels').get(url=url)
    except Board.DoesNotExist:
        raise Http404

    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(isPrivate=False)).distinct()
    developerProfiles = DeveloperProfile.objects.all().select_related('user')

    boardColumns = thisBoard.boardColumns.all()
    boardLabels = thisBoard.boardLabels.all()

    if request.is_ajax():
        # update board
        boardName = request.GET.get('board-name', None)
        boardVisibility = request.GET.get('board-visibility', None)

        addProject = request.GET.get('add-project', None)
        removeProject = request.GET.get('remove-project', None)

        addAdmin = request.GET.get('add-admin', None)
        removeAdmin = request.GET.get('remove-admin', None)

        addMember = request.GET.get('add-member', None)
        removeMember = request.GET.get('remove-member', None)


        # update column
        newColumnName = request.GET.get('new-column-name', None)

        removeColumn = request.GET.get('remove-column', None)

        updateColumnName = request.GET.get('update-column-name', None)
        columnId = request.GET.get('column-id', None)

        newColumnOrder = request.GET.getlist('new-column-order[]', None)

        # update label
        newLabelName = request.GET.get('new-label-name', None)

        removeLabel = request.GET.get('remove-label', None)

        updateLabelName = request.GET.get('update-label-name', None)
        updateLabelColour = request.GET.get('update-label-colour', None)
        labelId = request.GET.get('label-id', None)

        if labelId is not None:
            label = Label.objects.get(id=labelId, board=thisBoard)
            updateFields = []

            if updateLabelName is not None:
                label.name = updateLabelName
                updateFields.append('name')

            if updateLabelColour:
                label.colour = updateLabelColour
                updateFields.append('colour')

            label.save(update_fields=updateFields)


        if columnId is not None:
            column = Column.objects.get(id=columnId)
            updateFields = []

            if updateColumnName is not None:
                column.name = updateColumnName
                updateFields.append('name')

            column.save(update_fields=updateFields)

        if len(newColumnOrder) > 0:
            newColumnOrder = [int(i.split('-')[2]) for i in newColumnOrder]
            for i in boardColumns:
                i.orderNo = newColumnOrder.index(i.pk)
                i.save(update_fields=['orderNo'])

        if removeLabel is not None:
            Label.objects.filter(id=removeLabel).delete()

        if removeColumn is not None:
            # TODO: Before removing columns check if there are any ticket present in this column. see TutorProfileForm
            Column.objects.filter(id=removeColumn).delete()

        if newLabelName is not None:
            newLabel = Label.objects.create(
                board=thisBoard,
                name=newLabelName,
            )
            response = {
                'statusCode': HTTPStatus.OK,
                'id': newLabel.id,
                'name': newLabel.name,
                'colour': newLabel.colour
            }
            return JsonResponse(response)

        if newColumnName is not None:
            existingColumn = [i for i in boardColumns if i.name.lower() == newColumnName.lower()]
            if len(existingColumn) == 0:
                newColumn = Column.objects.create(
                    board=thisBoard,
                    name=newColumnName,
                    orderNo=thisBoard.boardColumns.count() + 1
                )
                response = {
                    'statusCode': HTTPStatus.OK,
                    'id': newColumn.id,
                    'name': newColumn.name,
                    'orderNo': newColumn.orderNo
                }
                return JsonResponse(response)

            else:
                response = {
                    'statusCode': HTTPStatus.ACCEPTED,
                }
                return JsonResponse(response)

        if boardName is not None:
            thisBoard.name = boardName

        if boardVisibility is not None:
            thisBoard.isPrivate = boardVisibility == 'visibility-members'

        if addProject is not None:
            _project = Project.objects.get(id=addProject)
            thisBoard.projects.add(_project)

        if removeProject is not None:
            _project = Project.objects.get(id=removeProject)
            thisBoard.projects.remove(_project)

        if addAdmin is not None:
            user = User.objects.get(id=addAdmin)
            thisBoard.admins.add(user)

        if removeAdmin is not None:
            user = User.objects.get(id=removeAdmin)
            thisBoard.admins.remove(user)

        if addMember is not None:
            user = User.objects.get(id=addMember)
            thisBoard.members.add(user)

        if removeMember is not None:
            user = User.objects.get(id=removeMember)
            thisBoard.members.remove(user)

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
