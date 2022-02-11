from django.contrib import admin

from jira2.forms import ProjectForm
from jira2.models import Board
from jira2.models import Column
from jira2.models import DeveloperProfile
from jira2.models import Label
from jira2.models import Project
from jira2.models import Sprint
from jira2.models import Team
from jira2.models import Ticket
from jira2.models import TicketAttachment
from jira2.models import TicketComment


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm


admin.site.register(Board)
admin.site.register(Column)
admin.site.register(DeveloperProfile)
admin.site.register(Label)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Sprint)
admin.site.register(Team)
admin.site.register(Ticket)
admin.site.register(TicketAttachment)
admin.site.register(TicketComment)
