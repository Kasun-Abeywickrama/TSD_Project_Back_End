from django.contrib import admin
from .models import CustomUser, Result

# Registering the custom user model
admin.site.register(CustomUser)
    
#registering the result model
admin.site.register(Result)


