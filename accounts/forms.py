from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages

from accounts.models import GetInTouch
from accounts.models import TutorProfile
from onetutor.operations import generalOperations


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Firstname'
            }
        )
    )
    last_name = forms.CharField(
        label='',
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
    # TODO: use password1 and password2 from super class.
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

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account already exists for this email address!")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Your passwords do not match!")

        if len(password1) < 8 or any(letter.isalpha() for letter in password1) == False or any(
                capital.isupper() for capital in password1) == False or any(
                number.isdigit() for number in password1) == False:
            raise forms.ValidationError("Your password is not strong enough.")

        return password1

    def save(self):
        newUser = User.objects.create_user(
            username=self.cleaned_data.get("email"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password1"),
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name")
        )
        newUser.is_active = settings.DEBUG
        newUser.save()
        return newUser

# TODO: extends AuthenticationForm
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
    rememberMe = forms.BooleanField(
        label='Remember Me',
        required=False,
        widget=forms.CheckboxInput()
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

            rememberMe = self.cleaned_data.get('rememberMe')
            if not rememberMe:
                self.request.session.set_expiry(0)

            return

        raise forms.ValidationError("Username or Password did not match! ")


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
        # TODO: make the fullName and email input side-by-side

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
            raise ValidationError(None)

        if not generalOperations.isPasswordStrong(newPassword):
            messages.warning(
                self.request,
                'Your new password is not strong enough.'
            )
            raise ValidationError(None)

        return self.cleaned_data

    def updatePassword(self):
        newPassword = self.cleaned_data.get('password')
        self.user.set_password(newPassword)
        self.user.save()


class TutorProfileForm(forms.ModelForm):
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
