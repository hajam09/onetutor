from datetime import (
    date,
    timedelta
)

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError

from core.models import Component
from onetutor.utils import utilsOperations
from profiles.models import (
    TutorProfile,
    StudentProfile,
    ParentProfile
)


class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ['summary', 'about', 'dateOfBirth', 'features']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get('summary').label = ''
        self.fields.get('summary').widget.attrs['placeholder'] = 'Summary'

        self.fields.get('about').label = ''
        self.fields.get('about').widget.attrs['placeholder'] = 'About'

        today = date.today()
        maxDate = today - timedelta(days=18 * 365.25)  # 16 years ago from today
        minDate = today - timedelta(days=100 * 365.25)  # 100 years ago from today

        self.fields.get('dateOfBirth').label = ''
        self.fields.get('dateOfBirth').help_text = 'You need be at least 16 years old to create tutor profile.'
        self.fields.get('dateOfBirth').widget = forms.DateInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Date-of-birth',
                'type': 'text',
                'required': '',
                'onfocus': '(this.type=\'date\')',
                'onblur': '(this.type=\'text\')',
                'min': minDate.strftime('%Y-%m-%d'),
                'max': maxDate.strftime('%Y-%m-%d')
            }
        )

        self.fields.get('features').label = ''
        self.fields.get('features').queryset = Component.objects.filter(
            componentGroup__code='TUTOR_FEATURE',
            adminOnly=False
        )

    def clean_dateOfBirth(self):
        if utilsOperations.isBelow18(self.cleaned_data.get('dateOfBirth')):
            raise ValidationError('Must be above 18 years old.')

        return self.cleaned_data.get('dateOfBirth')


class StudentProfileForm(forms.ModelForm):
    parentCode = forms.CharField(
        max_length=8,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'textinput form-control',
                'hidden': True,
                'placeholder': 'Parent code'
            }
        )
    )

    class Meta:
        model = StudentProfile
        fields = ['about', 'dateOfBirth', 'parentCode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get('about').label = ''
        self.fields.get('about').widget.attrs['placeholder'] = 'About'

        self.fields.get('dateOfBirth').label = ''
        self.fields.get('dateOfBirth').widget = forms.DateInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Date-of-birth',
                'type': 'text',
                'required': '',
                'onfocus': '(this.type=\'date\')',
                'onblur': '(this.type=\'text\')',
            }
        )

        self.fields.get('parentCode').label = ''

    def clean_parentCode(self):
        if utilsOperations.isBelow18(self.cleaned_data.get('dateOfBirth')):
            del self.fields.get('parentCode').widget.attrs['hidden']
            parentCode = self.cleaned_data.get('parentCode')
            if not ParentProfile.objects.filter(code__exact=parentCode).exists():
                raise ValidationError('No parent found for this code.')
        return self.cleaned_data.get('parentCode')


class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['dateOfBirth']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get('dateOfBirth').label = ''
        self.fields.get('dateOfBirth').widget = forms.DateInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Date-of-birth',
                'type': 'text',
                'required': '',
                'onfocus': '(this.type=\'date\')',
                'onblur': '(this.type=\'text\')',
            }
        )

    def clean_dateOfBirth(self):
        if utilsOperations.isBelow18(self.cleaned_data.get('dateOfBirth')):
            raise ValidationError('Must be above 18 years old.')

        return self.cleaned_data.get('dateOfBirth')


class CustomPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get('old_password').label = ''
        self.fields.get('old_password').widget.attrs['placeholder'] = 'Old password'

        self.fields.get('new_password1').label = ''
        self.fields.get('new_password1').widget.attrs['placeholder'] = 'New password'

        self.fields.get('new_password2').label = ''
        self.fields.get('new_password2').widget.attrs['placeholder'] = 'Confirm new password'
