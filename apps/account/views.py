from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.views.generic import CreateView
from django.views.generic.base import View
from django.urls import reverse_lazy

from apps.account.forms import RegistrationForm, SignInForm

User = get_user_model()


class RegistrationView(CreateView):

    """ Регистрация пользователя """

    model = User
    form_class = RegistrationForm
    template_name = 'account/registration.html'
    success_url = reverse_lazy('successful_registration')


class SuccessfulRegistrationView(View):

    """ Для успешно зарегистрированных пользователей. Перенаправление """

    def get(self, request):
        return render(request, 'account/successful_registration.html')


class AccountActivationView(View):

    """ Активация аккаунта пользователя """

    def get(self, request):
        code = request.GET.get('user')
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return render(request, 'account/activation.html')


class SignInView(LoginView):

    """ Авторизация пользователя """

    form_class = SignInForm
    template_name = 'account/login.html'
    success_url = reverse_lazy('index')
