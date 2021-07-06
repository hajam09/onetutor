from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
        newUser =  User.objects.create_user(
            username=self.cleaned_data.get("email"),
            email=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password1"),
            first_name=self.cleaned_data.get("first_name"),
            last_name=self.cleaned_data.get("last_name")
        )
        newUser.is_active = settings.DEBUG
        newUser.save()
        return newUser

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
    remember_me = forms.BooleanField(
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

        if not self.cleaned_data.get('remember_me', None):
            self.request.session.set_expiry(0)

        user = authenticate(username=email, password=password)
        if user:
            login(self.request, user)
            return

        raise forms.ValidationError("Username or Password did not match! ")
