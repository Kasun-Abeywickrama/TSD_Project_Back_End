from django.db import models
from django.contrib.auth.models import AbstractUser

#Creating a custom user model to store user information
class CustomUser(AbstractUser):
    # Add any additional fields needed
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)

    def __str__(self):
        return self.username


#creating the result model
class Result(models.Model):
    # Adding the foreign key field
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    #Adding the other fields
    test_score = models.CharField(max_length = 40)
    depression_level = models.CharField(max_length=100)
    no_of_days = models.CharField(max_length=20)
    final_result = models.CharField(max_length=200)
    test_taken_at = models.DateField(auto_now_add=True)
