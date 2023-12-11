from django.db.models.functions import TruncSecond
from django.db import models
from django.contrib.auth.models import AbstractUser

#Creating a custom user model to store authentication information
class AuthUser(AbstractUser):

    #Declaring the field to include the user type (user, counselor, admin)
    auth_user_type = models.CharField(max_length=50)

    def __str__(self):
        return self.username
    

#Creating the User model
class User(models.Model):

    #Declaring 1 to 1 relationship between AuthUser model
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    #Declaring relavant fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    telephone = models.CharField(max_length=50)
    age = models.CharField(max_length=3)

    def __str__(self):
        return self.first_name
    

#Creating the Question model
class Question(models.Model):

    question = models.CharField(max_length=200)
    selected_order = models.CharField(max_length=5)

    def __str__(self):
        return self.question
    


#Creating the answer model
class Answer(models.Model):

    #Foreign key of Question model
    question = models.ForeignKey(Question, on_delete= models.CASCADE)

    #Other fields
    answer = models.CharField(max_length=200)
    mark = models.CharField(max_length=30)

    def __str__(self):
        return self.answer




#Creating the quiz_rsult model to store quiz results
class QuizResult(models.Model):
    # Adding the foreign key field from the User table (1:many relationship)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Creating the many to many relationship between the question and quiz result table
    questions = models.ManyToManyField(Question, through='QuizQandA')

    #Adding the other fields
    score = models.CharField(max_length = 40)
    dp_level = models.CharField(max_length=100)
    no_of_days = models.CharField(max_length=20)
    conclusion = models.CharField(max_length=200)
    counselor_or_not = models.CharField(max_length=1)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    


# Creating the many to many table of question and quiz result
class QuizQandA(models.Model):
    #Foreign key with question model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    #Foreign key with the quiz result model
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE)

    #Adding the other fields
    answer_id = models.CharField(max_length=30)
