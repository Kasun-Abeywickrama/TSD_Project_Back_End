from rest_framework import serializers
from .models import Appointment, AuthUser, QuizQandA, QuizResult, User, Question, Answer

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
    
    def update(self, instance, validated_data):
        password = validated_data.get('password')
        if password:
            instance.set_password(password)

        instance.username = validated_data.get('username', instance.username)
        instance.auth_user_type = validated_data.get('auth_user_type', instance.auth_user_type)
        
        instance.save()
        return instance
    

#Creating the model serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile_number = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)


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




#creating the serializer to validate and store quiz result data
class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = '__all__'



#Creating the serializer to validate and store quiz questions and answers data
class QuizQandASerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQandA
        fields = '__all__'


#Creating the serializer to validate the quiz result id
class QuizResultSendingSerializer(serializers.Serializer):
    quiz_result_id = serializers.CharField()


#Creating the previous quiz result sending serializer
class PreviousQuizResultSendingSerializer(serializers.ModelSerializer):
    class Meta:
        model =  QuizResult
        fields = ['id', 'date', 'time', 'dp_level', 'score']


# creating the appointment serializer
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'





