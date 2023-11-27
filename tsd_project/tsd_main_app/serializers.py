from rest_framework import serializers
from .models import CustomUser

#Creating the serializer for custom user model
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'firstname', 'lastname']

    #Creating the hashed password to store in the database
    def create(self, validated_data):
        password = validated_data.pop('password')
        customuser = CustomUser(**validated_data)
        customuser.set_password(password)
        customuser.save()
        return customuser


#Creating a serializer to validate the login information
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


