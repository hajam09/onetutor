import re

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import GetInTouch
from accounts.models import TutorProfile
from onetutor.operations import generalOperations, databaseOperations

# TODO: password_validation.validate_password(password, self.instance) for better security
from tutoring.models import Component, Availability


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='',
        strip=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Firstname'
            }
        )
    )
    last_name = forms.CharField(
        label='',
        strip=True,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Lastname'
            }
        )
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email'
            }
        )
    )
    password1 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password'
            }
        )
    )
    password2 = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    USERNAME_FIELD = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('An account already exists for this email address!')

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Your passwords do not match!')

        if not generalOperations.isPasswordStrong(password1):
            raise ValidationError('Your password is not strong enough.')

        return password1

    @transaction.atomic
    def save(self):
        user = User()
        user.username = self.cleaned_data.get('email')
        user.email = self.cleaned_data.get('email')
        user.set_password(self.cleaned_data['password1'])
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.is_active = False
        user.save()
        return user


class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email'
            }
        )
    )
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password'
            }
        )
    )

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean_password(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        user = authenticate(username=email, password=password)
        if user:
            login(self.request, user)
            return self.cleaned_data

        raise ValidationError('Please enter a correct email and password.')


class GetInTouchForm(forms.ModelForm):
    fullName = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Full Name'
            }
        )
    )

    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Email'
            }
        )
    )

    subject = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Subject'
            }
        )
    )

    message = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Message',
                'rows': 3,
            }
        )

    )

    class Meta:
        model = GetInTouch
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(GetInTouchForm, self).__init__(*args, **kwargs)
        self.regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # TODO: make the fullName and email input side-by-side

    def clean(self):
        email = self.cleaned_data.get("email")

        if not re.fullmatch(self.regex, email):
            raise ValidationError('Your email address format is not correct.')

        return self.cleaned_data

    def save(self):
        GetInTouch.objects.create(
            fullName=self.cleaned_data.get("fullName"),
            email=self.cleaned_data.get("email"),
            subject=self.cleaned_data.get("subject"),
            message=self.cleaned_data.get("message")
        )


class PasswordChangeForm(forms.Form):
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password'
            }
        )
    )

    repeatPassword = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Repeat Password'
            }
        )
    )

    def __init__(self, request=None, user=None, *args, **kwargs):
        self.request = request
        self.user = user
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        newPassword = self.cleaned_data.get('password')
        confirmPassword = self.cleaned_data.get('repeatPassword')

        if newPassword != confirmPassword:
            messages.error(
                self.request,
                'Your new password and confirm password does not match.'
            )
            raise ValidationError('Your new password and confirm password does not match.')

        if not generalOperations.isPasswordStrong(newPassword):
            messages.warning(
                self.request,
                'Your new password is not strong enough.'
            )
            raise ValidationError('Your new password is not strong enough.')

        # TODO: use validate_password for better security.

        return self.cleaned_data

    def updatePassword(self):
        newPassword = self.cleaned_data.get('password')
        self.user.set_password(newPassword)
        self.user.save()


class TutorProfileCreateForm(forms.Form):
    summary = forms.CharField(
        label='Summary',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control col',
                'required': 'required',
            }
        ),
    )
    about = forms.CharField(
        label='About',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control col',
                'style': 'border-radius: 0',
                'required': 'required',
                'rows': 5,
            }
        )
    )
    chargeRate = forms.DecimalField(
        label='Charge Rate (£)',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'style': 'width: 100%',
                'required': 'required',
                'step': '0.1',
                'min': '0',
            }
        ),
    )
    teachingLevels = forms.MultipleChoiceField(
        label='Teaching levels',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'required': 'required',
                'multiple': 'multiple',
            }
        ),
    )
    tutorFeatures = forms.MultipleChoiceField(
        label='Features',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'required': 'required',
                'multiple': 'multiple',
            }
        ),
    )
    subjects = forms.MultipleChoiceField(
        label='Subjects',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2',
                'style': 'width: 100%;',
                'required': 'required',
                'multiple': 'multiple',
            }
        ),
    )

    def __init__(self, request, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(TutorProfileCreateForm, self).__init__(*args, **kwargs)
        self.request = request

        TEACHING_LEVEL_CHOICES = (
            (c.id, c.internalKey) for c in Component.objects.filter(componentGroup__code="EDUCATION_LEVEL")
        )
        FEATURE_CHOICES = (
            (c.id, c.internalKey) for c in Component.objects.filter(componentGroup__code="TUTOR_FEATURE")
        )

        self.base_fields['teachingLevels'].choices = TEACHING_LEVEL_CHOICES
        self.base_fields['tutorFeatures'].choices = FEATURE_CHOICES
        self.base_fields['subjects'].choices = ((1, "A"), (2, "B"))
        self.initial['initialEducationList'] = [
            (1, '', '', '', '')
        ]

    def clean(self):
        schoolNames = self.request.POST.getlist('schoolName')
        qualifications = self.request.POST.getlist('qualification')
        startDates = self.request.POST.getlist('startDate')
        endDates = self.request.POST.getlist('endDate')

        del self.errors['teachingLevels']
        del self.errors['tutorFeatures']
        del self.errors['subjects']

        isValid = not (schoolNames == [] or qualifications == [] or startDates == [] or endDates == [])
        enteredEducationList = []
        counter = 1
        for schoolName, qualification, startDate, endDate in zip(schoolNames, qualifications, startDates, endDates):
            enteredEducationList.append((counter, schoolName, qualification, startDate, endDate))
            thisRowValid = not (not schoolName or not qualification or not startDate or not endDate)
            counter += 1

            if not thisRowValid:
                isValid = False

        if not isValid:
            self.errors['initialEducationList'] = self.error_class(
                ['Please enter your education history.']
            )

        self.initial['initialEducationList'] = enteredEducationList
        self.cleaned_data['subjects'] = 'E1'

        return self.cleaned_data

    def save(self):
        schoolNames = self.data.getlist('schoolName')
        qualifications = self.data.getlist('qualification')
        startDates = self.data.getlist('startDate')
        endDates = self.data.getlist('endDate')
        databaseOperations.createEducationInBulk(self.request, schoolNames, qualifications, startDates, endDates)

        profile, created = TutorProfile.objects.update_or_create(
            user=self.request.user,
            defaults={
                'summary': self.cleaned_data.get('summary'),
                'about': self.cleaned_data.get('about'),
                'subjects': ', '.join([i.capitalize() for i in self.request.POST.getlist('subjects')]),
                'chargeRate': float(self.cleaned_data.get('chargeRate')),
            }
        )

        profile.features.clear()
        profile.teachingLevels.clear()

        profile.features.add(*[int(i) for i in self.data.getlist('tutorFeatures')])
        profile.teachingLevels.add(*[int(i) for i in self.data.getlist('teachingLevels')])

        Availability.objects.get_or_create(
            user=self.request.user
        )


class TutorProfileForm2(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = "__all__"

    def clean(self):
        """
        check that the component added is from the componentGroup.code = "TUTOR_FEATURE"
        At the moment the limit_choices_to in TutorProfile.features only show features.componentGroup.code = "TUTOR_FEATURE"
        """
        features = self.cleaned_data.get('features')
        if features:
            for f in features:
                if f.componentGroup.code != "TUTOR_FEATURE":
                    raise ValidationError("Only add component(s) which belong to the 'Tutor Feature' component group.")

        return self.cleaned_data


class UserSettingsPasswordUpdateForm(forms.Form):
    currentPassword = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Current password'
            }
        )
    )
    newPassword = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'New password'
            }
        )
    )
    repeatNewPassword = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Repeat new password'
            }
        )
    )

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.user = request.user
        super(UserSettingsPasswordUpdateForm, self).__init__(*args, **kwargs)

    def clean(self):
        currentPassword = self.cleaned_data.get('currentPassword')
        newPassword = self.cleaned_data.get('newPassword')
        repeatNewPassword = self.cleaned_data.get('repeatNewPassword')

        # TODO: use validate_password for better security.

        if currentPassword and not self.user.check_password(currentPassword):
            raise ValidationError('Your current password does not match with the account\'s existing password.')

        if newPassword and repeatNewPassword:
            if newPassword != repeatNewPassword:
                raise ValidationError('Your new password and confirm password does not match.')

            if not generalOperations.isPasswordStrong(newPassword):
                raise ValidationError('Your new password is not strong enough.')

        return self.cleaned_data

    def updatePassword(self):
        newPassword = self.cleaned_data.get('newPassword')
        self.user.set_password(newPassword)
        self.user.save()

    def reAuthenticate(self, signIn):
        newPassword = self.cleaned_data.get('newPassword')
        user = authenticate(username=self.user.username, password=newPassword)
        if user:
            messages.success(
                self.request,
                'Your password has been updated.'
            )
            signIn(self.request, user)
            return True
        else:
            messages.warning(
                self.request,
                'Something happened. Try to login to the system again.'
            )
            return False


class EducationForm(forms.Form):
    schoolName = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'School Name',
                'data - toggle': 'tooltip',
                'data - placement': 'top',
                'title': 'School Name',
            }
        )
    )
    qualifications = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Qualification & Grade(s)s',
                'data - toggle': 'tooltip',
                'data - placement': 'top',
                'title': 'Qualification & Grade(s)',
            }
        )
    )
    startDate = forms.DateField(
        label='',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'month',
                'data - toggle': 'tooltip',
                'data - placement': 'top',
                'title': 'Attended from',
            }
        )
    )
    endDate = forms.DateField(
        label='',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'month',
                'data - toggle': 'tooltip',
                'data - placement': 'top',
                'title': 'Attended to',
            }
        )
    )
