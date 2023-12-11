from django.contrib import admin
from .models import AuthUser, QuizQandA, QuizResult, User, Question, Answer

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


