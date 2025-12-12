from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class User(AbstractUser):
    username = None  # Username field disabled
    email = models.EmailField("email address", unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    
    institution = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default

    objects = CustomUserManager() # type: ignore # Links manager

    def __str__(self):
        return self.email