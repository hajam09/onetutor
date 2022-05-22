from http import HTTPStatus

from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render

from jira2.models import *
from onetutor.operations import databaseOperations


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
    """
    privateAdminProjects = Project.objects.filter(isPrivate=True, members__in=[request.user]).select_related('lead__developerProfile', 'status')
    nonPrivateProjects = Project.objects.filter(isPrivate=False).select_related('lead__developerProfile', 'status')
    allProjects = ( privateAdminProjects | nonPrivateProjects ).distinct()
    """

    allProjects = Project.objects.filter(Q(isPrivate=True, members__in=[request.user]) | Q(isPrivate=False)).select_related('lead__developerProfile', 'status').distinct()
    developerProfiles = DeveloperProfile.objects.select_related('user').all()

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

        # TODO: Bug in the key.
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


def projectSettings(request, url):

    """
    TODO: The start date and the end date in the template is not showing the correct project dates.
    TODO: Disable the project description at first and then activate it on click.
    TODO: Display all the kanban boards that link this project.
    """

    try:
        thisProject = Project.objects.get(url=url)
    except Project.DoesNotExist:
        raise Http404

    developerProfiles = DeveloperProfile.objects.select_related('user').all()
    projectStatusComponent = Component.objects.filter(componentGroup__internalKey='Project Status')

    if request.method == "POST":
        thisProject.name = request.POST['project-name']
        thisProject.code = request.POST['project-code']
        thisProject.description = request.POST['project-description']
        thisProject.startDate = request.POST['project-start']
        thisProject.endDate = request.POST['project-end']
        thisProject.isPrivate = request.POST['project-visibility'] == 'visibility-members'
        thisProject.lead = next((dp.user for dp in developerProfiles if str(dp.user.id) == request.POST['project-lead']), None) #User.objects.get(id=request.POST['project-lead'])
        thisProject.status = next((psc for psc in projectStatusComponent if str(psc.id) == request.POST['project-status']), None)

        updatedIcon = request.FILES.get('project-icon', None)
        if updatedIcon is not None:
            thisProject.icon = updatedIcon

        # TODO: Consider fetching User objects from db directly if it would reduce computation time.
        updatedProjectMembers = [i.user for i in developerProfiles if str(i.user.id) in request.POST.getlist('project-members')]
        thisProject.members.clear()
        thisProject.members.add(*updatedProjectMembers)

        thisProject.save()

    context = {
        'project': thisProject,
        'developerProfiles': developerProfiles,
        'projectStatusComponent': projectStatusComponent
    }
    return render(request, 'jira2/projectSettings.html', context)


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

        # need to create a backlog column when creating a board.
        Column.objects.create(
            board=newBoard,
            name='Backlog',
            deleteFl=True
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
    try:
        thisBoard = Board.objects.get(url=url)
    except Board.DoesNotExist:
        raise Http404

    if thisBoard.isPrivate:
        if not request.user in thisBoard.members.all() or not request.user in thisBoard.admins.all():
            # bad request, do not show the board to this user.
            pass

    boardColumns = thisBoard.boardColumns.all().exclude(name__icontains="Backlog", orderNo=1)
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
            label = databaseOperations.getObjectByIdOrNone(boardLabels, labelId)
            updateFields = []

            if updateLabelName is not None:
                label.name = updateLabelName
                updateFields.append('name')

            if updateLabelColour:
                label.colour = updateLabelColour
                updateFields.append('colour')

            label.save(update_fields=updateFields)


        if columnId is not None:
            column = databaseOperations.getObjectByIdOrNone(boardColumns, columnId)
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
            _project = databaseOperations.getObjectByIdOrNone(allProjects, addProject)
            thisBoard.projects.add(_project)

        if removeProject is not None:
            _project = databaseOperations.getObjectByIdOrNone(allProjects, removeProject)
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
    """
    TODO: change internalKey -> url in the arguments
    TODO: think about Ticket.column and Ticket.status
    """
    try:
        thisTicket = Ticket.objects.select_related('issueType', 'project', 'priority').prefetch_related('epicTickets__issueType', 'epicTickets__assignee', 'epicTickets__priority').get(internalKey__iexact=internalKey)
    except Ticket.DoesNotExist:
        raise Http404

    # if not internalKey == "{}-{}".format(thisTicket.project.code, thisTicket.id):
    #     raise Http404

    jiraIssues = Component.objects.filter(componentGroup__internalKey="Ticket Issue Type").exclude(internalKey="Epic")
    jiraPriorities = Component.objects.filter(componentGroup__internalKey="Ticket Priority")

    if thisTicket.issueType.code == 'EPIC':
        TEMPLATE_NAME = 'jira2/epicTicketPage.html'
    else:
        TEMPLATE_NAME = 'jira2/standardTicketPage.html'

    if request.is_ajax():
        updateTicketSummary = request.GET.get('update-ticket-summary', None)
        updateTicketDescription = request.GET.get('update-ticket-description', None)
        updateTicketUserImpact = request.GET.get('update-ticket-user-impact', None)
        updateTicketReleaseImpact = request.GET.get('update-ticket-release-impact', None)
        updateTicketAutomaticTestingReason = request.GET.get('update-ticket-automatic-testing-reason', None)
        newTicket = request.GET.get('new-ticket', None)
        newSubTicket = request.GET.get('new-sub-ticket', None)
        newIssueName = request.GET.get('new-issue-name', None)
        newIssueType = request.GET.get('new-issue-type', None)
        updateTicketPriority = request.GET.get('update-ticket-priority', None)
        functionality = request.GET.get('functionality', None)

        if updateTicketPriority is not None:
            thisTicket.priority = next(i for i in jiraPriorities if i.code==updateTicketPriority)

        if updateTicketSummary is not None:
            thisTicket.summary = updateTicketSummary

        if updateTicketDescription is not None:
            thisTicket.description = updateTicketDescription

        if updateTicketUserImpact is not None:
            thisTicket.userImpact = updateTicketUserImpact

        if updateTicketReleaseImpact is not None:
            thisTicket.releaseImpact = updateTicketReleaseImpact

        if updateTicketAutomaticTestingReason is not None:
            thisTicket.automatedTestingReason = updateTicketAutomaticTestingReason

        ticketProject = thisTicket.project
        newTicketNumber = ticketProject.projectTickets.count() + 1

        if newTicket is not None:
            Ticket(
                internalKey=ticketProject.name + "-" + str(newTicketNumber),
                summary=newTicket,
                project=ticketProject,
                assignee=request.user,
                issueType=request.user,
            )

        if newSubTicket is not None:
            # this is only created in normal ticket type and not in an epic ticket.
            newSubTicketObj = Ticket.objects.create(
                internalKey=ticketProject.code + "-" + str(newTicketNumber),
                summary=newSubTicket,
                project=ticketProject,
                sprint=thisTicket.sprint,
                reporter=request.user,
                issueType=Component.objects.get(componentGroup__code='TICKET_ISSUE_TYPE', code='SUB_TASK'),
                securityLevel=Component.objects.get(componentGroup__code='TICKET_SECURITY', code='INTERNAL'),
                status=thisTicket.status,
                priority=Component.objects.get(componentGroup__code='TICKET_PRIORITY', code='MEDIUM'),
                board=thisTicket.board,
                column=thisTicket.column,
            )
            thisTicket.subTask.add(newSubTicketObj)

            response = {
                'statusCode': HTTPStatus.OK,
                'id': newSubTicketObj.id,
                'internalKey': newSubTicketObj.internalKey,
                'summary': newSubTicketObj.summary,
                'priority': {
                    'internalKey': newSubTicketObj.priority.internalKey,
                    'icon': newSubTicketObj.priority.icon,
                },
                'issueType': {
                    'internalKey': newSubTicketObj.issueType.internalKey,
                    'icon': newSubTicketObj.issueType.icon
                }
            }
            return JsonResponse(response)

        if newIssueName and newIssueType:
            ticketProject = thisTicket.project
            newTicket = Ticket.objects.create(
                internalKey=ticketProject.code + "-" + str(newTicketNumber),
                summary=newIssueName,
                project=ticketProject,
                reporter=request.user,
                issueType=next((i for i in jiraIssues if i.code==newIssueType), None),
                securityLevel=Component.objects.get(componentGroup__internalKey="Ticket Security", internalKey="External"),
                status=Component.objects.get(componentGroup__internalKey="Ticket Status", internalKey="Backlog"),
                priority=Component.objects.get(componentGroup__code='TICKET_PRIORITY', code='MEDIUM'),
                board=thisTicket.board,
                column=thisTicket.column,
                epic=thisTicket,
            )

            response = {
                'statusCode': HTTPStatus.OK,
                'id': newTicket.id,
                'internalKey': newTicket.internalKey,
                'summary': newTicket.summary,
                'issueType': {
                    'internalKey': newTicket.issueType.internalKey,
                    'icon': newTicket.issueType.icon
                },
                'priority': {
                    'internalKey': newTicket.priority.internalKey,
                    'icon': newTicket
                        .priority.icon,
                },
            }
            return JsonResponse(response)

        # if functionality == 'updateEpicTicketsOrder':
        #     newColumnOrder = request.GET.getlist('new-column-order[]', None)
        #     newColumnOrder = [int(i.split('-')[-1]) for i in newColumnOrder]
        #     oldOrderNo = [i.orderNo for i in thisTicket.epicTickets.all()]
        #     updatedObjects = []
        #
        #     counter = -1
        #     for et in thisTicket.epicTickets.all():
        #         counter += 1
        #         if et.id == newColumnOrder[counter]:
        #             continue
        #
        #         indexOf = newColumnOrder.index(et.id)
        #         et.orderNo = oldOrderNo[indexOf]
        #         updatedObjects.append(et)
        #
        #     Ticket.objects.bulk_update(updatedObjects, ['orderNo'])

        thisTicket.save()

    context = {
        'ticket': thisTicket,
        'jiraIssues': jiraIssues,
        'jiraPriorities': jiraPriorities,
    }
    return render(request, TEMPLATE_NAME, context)


def kanbanBoard(request, internalKey):
    return render(request, "jira2/kanbanBoard.html")
