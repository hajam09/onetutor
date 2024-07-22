from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    SetPasswordForm
)
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields.get('username').label = ''
        self.fields.get('username').widget.attrs['placeholder'] = 'Username'
        self.fields.get('password').label = ''
        self.fields.get('password').widget.attrs['placeholder'] = 'Password'

    def get_invalid_login_error(self):
        raise ValidationError({'password': super(LoginForm, self).get_invalid_login_error().messages})


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get('first_name').widget.attrs['placeholder'] = 'First Name'
        self.fields.get('last_name').widget.attrs['placeholder'] = 'Last Name'
        self.fields.get('username').widget.attrs['placeholder'] = 'Username'
        self.fields.get('email').widget.attrs['placeholder'] = 'Email'
        self.fields.get('password1').widget.attrs['placeholder'] = 'Password'
        self.fields.get('password2').widget.attrs['placeholder'] = 'Confirm Password'

        self.fields.get('first_name').required = True
        self.fields.get('last_name').required = True
        self.fields.get('username').required = True
        self.fields.get('email').required = True
        self.fields.get('password1').required = True
        self.fields.get('password2').required = True

        self.fields.get('first_name').label = ''
        self.fields.get('last_name').label = ''
        self.fields.get('username').label = ''
        self.fields.get('email').label = ''
        self.fields.get('password1').label = ''
        self.fields.get('password2').label = ''

        self.fields.get('first_name').widget.attrs['autofocus'] = True
        self.fields.get('username').widget.attrs['autofocus'] = False

        self.fields.get('username').help_text = None
        self.fields.get('password1').help_text = None
        self.fields.get('password2').help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        if commit:
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields.get('new_password1').widget.attrs['placeholder'] = 'Password'
        self.fields.get('new_password2').widget.attrs['placeholder'] = 'Confirm Password'

        self.fields.get('new_password1').label = ''
        self.fields.get('new_password2').label = ''

        self.fields.get('new_password1').widget.attrs['autofocus'] = True

        self.fields.get('new_password1').help_text = None
        self.fields.get('new_password2').help_text = None
