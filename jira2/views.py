from django.db.models import Q
from django.http import Http404
from django.shortcuts import render

from jira2.models import *


def dashboard(request):
    return render(request, "jira2/dashboard.html")


def backlog(request, url):
    try:
        board = Board.objects.get(url=url)
    except Board.DoesNotExist:
        raise Http404

    context = {
        "board": board
    }
    return render(request, 'jira2/backLog.html', context)


def projects(request):
    """
    TODO: Filter dropdown to filter projects by name, name contains, lead, status (show ongoing and terminated)...
    """
    """
    privateAdminProjects = Project.objects.filter(isPrivate=True, members__in=[request.user]).select_related('lead__developerProfile', 'status')
    nonPrivateProjects = Project.objects.filter(isPrivate=False).select_related('lead__developerProfile', 'status')
    allProjects = ( privateAdminProjects | nonPrivateProjects ).distinct()
    """

    allProjects = Project.objects.filter(
        Q(isPrivate=True, members__in=[request.user]) | Q(isPrivate=False)).select_related('lead__developerProfile',
                                                                                           'status').distinct()
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
        thisProject.lead = next(
            (dp.user for dp in developerProfiles if str(dp.user.id) == request.POST['project-lead']),
            None)  # User.objects.get(id=request.POST['project-lead'])
        thisProject.status = next(
            (psc for psc in projectStatusComponent if str(psc.id) == request.POST['project-status']), None)

        updatedIcon = request.FILES.get('project-icon', None)
        if updatedIcon is not None:
            thisProject.icon = updatedIcon

        # TODO: Consider fetching User objects from db directly if it would reduce computation time.
        updatedProjectMembers = [i.user for i in developerProfiles if
                                 str(i.user.id) in request.POST.getlist('project-members')]
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

    privateAdminBoards = Board.objects.filter(isPrivate=True, admins__in=[request.user]).prefetch_related('projects',
                                                                                                          'admins__developerProfile')
    privateMemberBoards = Board.objects.filter(isPrivate=True, members__in=[request.user]).prefetch_related('projects',
                                                                                                            'admins__developerProfile')
    nonPrivateBoards = Board.objects.filter(isPrivate=False).prefetch_related('projects', 'admins__developerProfile')

    allBoards = (privateAdminBoards | privateMemberBoards | nonPrivateBoards).distinct()
    developerProfiles = DeveloperProfile.objects.all().select_related('user')
    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(
        isPrivate=False)).distinct()

    if request.method == "POST":
        boardAdmins = [i.user for i in developerProfiles if str(i.user.pk) in request.POST.getlist('board-admins')]
        boardMembers = [i.user for i in developerProfiles if str(i.user.pk) in request.POST.getlist('board-members')]
        boardProjects = [i for i in allProjects if str(i.pk) in request.POST.getlist('board-projects')]

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
    context = {
        "board": thisBoard
    }
    return render(request, "jira2/board.html", context)


def boardSettings(request, url):
    try:
        thisBoard = Board.objects.prefetch_related('boardColumns', 'boardLabels').get(url=url)
    except Board.DoesNotExist:
        raise Http404

    allProjects = (Project.objects.filter(isPrivate=True, members__in=[request.user]) | Project.objects.filter(
        isPrivate=False)).distinct()
    developerProfiles = DeveloperProfile.objects.all().select_related('user')

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
        thisTicket = Ticket.objects.select_related('issueType', 'project', 'priority').prefetch_related(
            'epicTickets__issueType', 'epicTickets__assignee', 'epicTickets__priority').get(
            internalKey__iexact=internalKey)
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
        updateTicketPriority = request.GET.get('update-ticket-priority', None)

        if updateTicketPriority is not None:
            thisTicket.priority = next(i for i in jiraPriorities if i.code == updateTicketPriority)

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
