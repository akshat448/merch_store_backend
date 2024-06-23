from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager

USER_POSITION_CHOICES = [
    ('MB','Member'),
    ('CR','Core'),
    ('JS','Joint Secretary'),
    ('FS','Finance Secretary'),
    ('GS','General Secretary'),
]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15, null=True, default=None, blank=True)
    name = models.CharField(max_length=100, null=True, default=None, blank=True)
    position = models.CharField(max_length=2, choices=USER_POSITION_CHOICES, default='MB')
    token = models.CharField(max_length=500, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email