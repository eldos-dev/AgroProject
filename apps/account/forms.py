from django.contrib.auth import get_user_model, authenticate
from django import forms
from django.core.exceptions import ValidationError

from apps.account.utils import send_activation_mail


User = get_user_model()


class RegistrationForm(forms.ModelForm):

    """ Форма для регистраци пользователя """

    password = forms.CharField(required=True, widget=forms.PasswordInput)
    password_confirmation = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password_confirmation']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует!')
        return email

    def clean(self):
        data = self.cleaned_data
        password = data.get('password')
        password_confirmation = data.pop('password_confirmation')
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен быть не менее 8 символов')
        if password != password_confirmation:
            raise forms.ValidationError('Пароли не совпадают')
        return data

    def save(self, commit=False):
        user = User.objects.create(**self.cleaned_data)
        send_activation_mail(user)
        return user


class SignInForm(forms.ModelForm):

    """ Форма для авторизации пользователя """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)


    class Meta:
        model = User
        fields = ['email', 'password']


    def clean(self):
        username = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError('Ваш адрес электронной почты с данным паролем не совпадает.')
                # raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(self.error_messages['inactive'], code='inactive',)


    def get_user(self):
        return self.user_cache


    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )