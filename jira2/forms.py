from django import forms
from django.contrib.auth.models import User

from jira2.models import Board
from jira2.models import DeveloperProfile
from jira2.models import Project
from jira2.models import Ticket
from tutoring.models import Component


class TicketForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        epicComponent = Component.objects.get(componentGroup__code='TICKET_ISSUE_TYPE', code='EPIC')
        self.fields['epic'].queryset = Ticket.objects.filter(issueType=epicComponent)


class ProjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        developerProfileUserIds = DeveloperProfile.objects.all().values_list('user__id', flat=True)
        users = User.objects.filter(id__in=developerProfileUserIds)
        self.fields['lead'].queryset = users
        self.fields['members'].queryset = users
        self.fields['watchers'].queryset = users

    class Meta:
        model = Project
        fields = "__all__"


class BoardForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BoardForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Board
        fields = "__all__"

    def clean(self):
        """
        TODO: create a backlog column when a new board is created
        """
        pass
