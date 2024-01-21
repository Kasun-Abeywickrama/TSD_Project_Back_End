from django.db.models.functions import TruncSecond
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.db import models

# Model for Page
class Page(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    image = models.CharField(max_length=200)
    fe_route = models.CharField(max_length=200, null=True)


    def __str__(self):
        return self.title

# Model for Role
class Role(models.Model):
    name = models.CharField(max_length=200) 
    pages = models.ManyToManyField(Page, through='RolePage')

    def __str__(self):
        return self.name

# Model for RolePage
class RolePage(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    create = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return 'Role: ' + self.role.name + ' -------------> Page: ' + self.page.title


#Creating a custom user model to store authentication information
class AuthUser(AbstractUser):

    #Declaring the field to include the user type (patient, admin)
    auth_user_type = models.CharField(max_length=50)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    age = models.IntegerField(null = True)

    def __str__(self):
        return self.username
    

#Creating the Patient model
class Patient(models.Model):

    #Declaring 1 to 1 relationship between AuthUser model
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    #Declaring relavant fields
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    mobile_number = models.CharField(max_length=50, null=True)
    date_of_birth = models.DateField(null=True)
    
    #We can access the age property through an instance of a Patient object
    @property
    def age(self):
        if self.date_of_birth is not None:
            today = date.today()
            age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            return age
        else:
            return "No Date of Birth"
        
    def __str__(self):
        return str(self.id)
            

#Creating the Question model
class Question(models.Model):

    question = models.CharField(max_length=200)
    selected_order = models.CharField(max_length=5)
    is_updating = models.BooleanField(default = False)
    last_updated_timestamp = models.DateTimeField(null = True)

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


#Creating the quiz_result model to store quiz results
class QuizResult(models.Model):
    # Adding the foreign key field from the patient table (1:many relationship)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

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
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.patient.first_name + " " + self.patient.last_name
    


# Creating the many to many table of question and quiz result
class QuizQandA(models.Model):
    #Foreign key with question model
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    #Foreign key with the quiz result model
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE)

    #Adding the other fields
    answer_id = models.CharField(max_length=30)

    def __str__(self):
        return self.id



#Creating the Admin model
class Admin(models.Model):

    #Declaring 1 to 1 relationship between AuthUser model
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)

    #Declaring the many to many relationship with the quiz result table
    quiz_result = models.ManyToManyField(QuizResult, through='Appointment')

    #Declaring relavant fields
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    mobile_number = models.CharField(max_length=50, null=True)
    location = models.CharField(max_length=200, null=True)
    website = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


# Creating the Appointment table 
class Appointment(models.Model):

    #Foreign key of the quiz result model
    quiz_result = models.ForeignKey(QuizResult, on_delete=models.CASCADE)

    #Foreign key of the admin model
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

    #Declaring the relavant fields
    requested_date = models.DateField(auto_now_add=True)
    is_checked = models.BooleanField()
    scheduled_date = models.DateField(null=True)
    scheduled_time_period = models.CharField(max_length = 100, null = True)
    response_description = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return str(self.quiz_result.user.first_name + " " + self.quiz_result.user.last_name)








    

