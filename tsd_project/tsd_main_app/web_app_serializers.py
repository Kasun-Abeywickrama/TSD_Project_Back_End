from rest_framework import serializers
from .models import AuthUser, Page

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'auth_user_type']
       

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

        
