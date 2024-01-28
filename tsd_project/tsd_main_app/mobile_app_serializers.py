from rest_framework import serializers
from .models import Appointment, AuthUser, PrivateQuestions, QuizQandA, QuizResult, Patient, Question, Answer

#Creating the model serializer for auth user model
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password','auth_user_type', 'role']

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
        instance.role = validated_data.get('role', instance.role)
        
        instance.save()
        return instance
    

#Creating the model serializer for Patient model
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile_number = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)


#Creating a serializer to validate the login information
class PatientLoginSerializer(serializers.Serializer):
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

# creating private questions serializer
class PrivateQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateQuestions
        fields = '__all__'





