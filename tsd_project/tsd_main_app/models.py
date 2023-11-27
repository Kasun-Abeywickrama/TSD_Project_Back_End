from django.db import models
from django.contrib.auth.models import AbstractUser

#Creating a custom user model to store user information
class CustomUser(AbstractUser):
    # Add any additional fields needed
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)

    def __str__(self):
        return self.username



