from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models



class UserManager(BaseUserManager):

    """ Создал кастомный UserManager """

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Электронная почта обязательна')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_superuser') is False:
            raise ValueError('У суперпользователей должно быть is_superuser=True')
        return self._create_user(email, password, **extra_fields)



class User(AbstractBaseUser):

    """ Переопределил встроенный класс User """

    activation_code = models.CharField(max_length=18, blank=True)
    email = models.EmailField(max_length=100, primary_key=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_staff

    def create_activation_code(self):
        from django.utils.crypto import get_random_string
        code = get_random_string(18)
        if User.objects.filter(activation_code=code).exists():
            self.create_activation_code()
        self.activation_code = code
        print(self.activation_code)
        self.save(update_fields=['activation_code'])

    def __str__(self):
        return f'{self.first_name} {self.last_name}'