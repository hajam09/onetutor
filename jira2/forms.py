from django import forms
from django.contrib.auth.models import User

from jira2.models import DeveloperProfile
from jira2.models import Project


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
