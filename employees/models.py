from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractUser

from employees.managers import CustomUserManager


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=225, blank=True, null=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=225)
    last_name = models.CharField(max_length=225)
    company = models.ForeignKey(
        Company, related_name="employees", on_delete=models.CASCADE
    )
    profile_pic = models.ImageField(
        upload_to="profile_pics/", default="profile_pics/default.jpeg"
    )
    email_address = models.EmailField(unique=True)

    def __str__(self):
        return self.first_name
