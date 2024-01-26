from django.contrib import admin
from .models import Appointment, AuthUser, Page, QuizQandA, QuizResult, Role, RolePage, Patient, Question, Answer, Admin, PrivateQuestions

# Registering the custom user model
admin.site.register(AuthUser)

#Registering the Patient model
admin.site.register(Patient)

#Resgistering the Question model
admin.site.register(Question)

#Registering the Answer model
admin.site.register(Answer)
    
#registering the quiz result model
admin.site.register(QuizResult)

#registering the quiz questions and answers model
admin.site.register(QuizQandA)

#registering the Admin model
admin.site.register(Admin)  

#registering the Permission model
admin.site.register(Role)  

#registering the Page model
admin.site.register(Page)  

# registering the Page model
admin.site.register(RolePage) 

#registering the appointment model
admin.site.register(Appointment)

#registering private questions model
admin.site.register(PrivateQuestions)
