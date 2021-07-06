from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import authenticate


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
