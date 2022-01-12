from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Thread, ChatMessage

admin.site.register(ChatMessage)


class ChatMessage(admin.TabularInline):
    model = ChatMessage


# class ThreadForm(forms.ModelForm):
#     def clean(self):
#         """
#         This is the function that can be used to
#         validate your model data from admin
#         """
#         super(ThreadForm, self).clean()
#         firstParticipant = self.cleaned_data.get('firstParticipant')
#         secondParticipant = self.cleaned_data.get('secondParticipant')
#
#         lookup1 = Q(firstParticipant=firstParticipant) & Q(secondParticipant=secondParticipant)
#         lookup2 = Q(firstParticipant=secondParticipant) & Q(secondParticipant=firstParticipant)
#         lookup = Q(lookup1 | lookup2)
#         qs = Thread.objects.filter(lookup)
#         if qs.exists():
#             raise ValidationError(f'Thread between {firstParticipant} and {secondParticipant} already exists.')
#

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)