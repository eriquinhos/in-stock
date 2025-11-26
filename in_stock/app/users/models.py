from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone

# class CustomUser(AbstractBaseUser, PermissionsMixin):
# email = models.EmailField(unique=True)
# TYPE_CHOICES = [
# ('admin', 'Administrador'),
# ('standard', 'Padrão'),
# ]
# type = models.CharField(max_length=8, choices=TYPE_CHOICES, default='standard')
# phone = models.CharField(max_length=20, blank=True, null=True)

# USERNAME_FIELD = 'email'
# REQUIRED_FIELDS = []  # se quiser adicionar outros campos obrigatórios, como 'phone'

# def __str__(self):
# return self.email


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O campo email é obrigatório")
        email = self.normalize_email(email).lower()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150, default="User")
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    TYPE_CHOICES = [
        ("admin", "Administrador"),
        ("standard", "Padrão"),
    ]
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, default="standard")
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
