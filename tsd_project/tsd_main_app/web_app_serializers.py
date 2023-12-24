from rest_framework import serializers
from .models import AuthUser, Page, Role

# class AdminUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AuthUser
#         fields = ['id', 'username', 'auth_user_type']

#Creating the model serializer for auth user model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password', 'auth_user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        authuser = AuthUser(**validated_data)
        authuser.set_password(password)
        authuser.save()
        return authuser

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.username = validated_data.get('username', instance.username)
        instance.auth_user_type = validated_data.get('auth_user_type', instance.auth_user_type)

        instance.save()
        return instance
       

# Creating serializer for the Page Model
class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


# Creating serializer for the Role Model
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


