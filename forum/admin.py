from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from forum.models import (
    Category,
    Thread,
    Comment
)


class ThreadAdminForm(forms.ModelForm):
    class Meta:
        model = Thread
        exclude = []

    likes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Likes'),
            is_stacked=False
        )
    )
    dislikes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Dislikes'),
            is_stacked=False
        )
    )
    watchers = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Watchers'),
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super(ThreadAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        thread = super(ThreadAdminForm, self).save(commit=False)
        thread.save()
        self.save_m2m()
        return thread


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = []

    likes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Likes'),
            is_stacked=False
        )
    )
    dislikes = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Dislikes'),
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super(CommentAdminForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super(CommentAdminForm, self).save(commit=False)
        comment.save()
        self.save_m2m()
        return comment


class ThreadAdmin(admin.ModelAdmin):
    form = ThreadAdminForm


class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm


admin.site.register(Category)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Comment, CommentAdmin)
