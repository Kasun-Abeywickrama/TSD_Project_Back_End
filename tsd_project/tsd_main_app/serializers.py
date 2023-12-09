from rest_framework import serializers
from .models import AuthUser, User, Question, Answer

#Creating the model serializer for auth user model
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password','auth_user_type']

    #Creating the hashed password to store in the database
    def create(self, validated_data):
        password = validated_data.pop('password')
        authuser = AuthUser(**validated_data)
        authuser.set_password(password)
        authuser.save()
        return authuser
    

#Creating the model serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','age', 'email', 'telephone', 'auth_user']

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    age = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    telephone = serializers.CharField(required=False)


#Creating a serializer to validate the login information
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



# Creating the answer sending serializer
class AnswerSendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer', 'mark']


# Creating the question sending serializer
class QuestionSendingSerializer(serializers.ModelSerializer):
    answers = AnswerSendingSerializer(many = True, read_only = True, source = 'answer_set')

    class Meta:
        model = Question
        fields = ['id', 'question', 'answers']







#creating the serializer to validate and store result data
#class ResultSerializer(serializers.ModelSerializer):
    #class Meta:
        #model = Result
        #fields = '__all__'


#Creating the serializer to validate the date and time of the result data
#lass ViewResultSerializer(serializers.Serializer):
    #date = serializers.DateField()
    #time = serializers.TimeField()


