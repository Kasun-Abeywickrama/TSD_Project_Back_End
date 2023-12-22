from django.contrib import admin
from .models import AuthUser, Page, Permission, QuizQandA, QuizResult, Role, User, Question, Answer, Admin

# Registering the custom user model
admin.site.register(AuthUser)

#Registering the User model
admin.site.register(User)

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
admin.site.register(Permission)  

#registering the Role model
admin.site.register(Role)  

#registering the Page model
admin.site.register(Page)  


