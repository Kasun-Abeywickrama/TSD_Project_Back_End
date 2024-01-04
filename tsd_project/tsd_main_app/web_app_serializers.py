from rest_framework import serializers
from .models import AuthUser, Page, Role, Question, Answer, QuizResult

#Creating the model serializer for auth user model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password', 'auth_user_type','role']
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


# Serializer for the Permission model, exposing all fields
class RoleSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)
    class Meta:
        model = Role
        fields = 'id', 'name', 'pages'


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = '__all__'

