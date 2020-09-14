from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from chat.models import Thread


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = "__all__"

    def clean(self):
        """
        check if a thread exists between firstParticipant and secondParticipant
        """
        super(ThreadForm, self).clean()
        firstParticipant = self.cleaned_data.get('firstParticipant')
        secondParticipant = self.cleaned_data.get('secondParticipant')

        lookup1 = Q(firstParticipant=firstParticipant) & Q(secondParticipant=secondParticipant)
        lookup2 = Q(firstParticipant=secondParticipant) & Q(secondParticipant=firstParticipant)
        lookup = Q(lookup1 | lookup2)

        thread = Thread.objects.filter(lookup)
        if thread.exists():
            # unique_together in Meta class should already alert the user. Additional validation.
            raise ValidationError(f'Thread between {firstParticipant} and {secondParticipant} already exists.')

        return self.cleaned_data
