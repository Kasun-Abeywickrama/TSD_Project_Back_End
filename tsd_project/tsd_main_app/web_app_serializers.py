from rest_framework import serializers
from .models import Appointment, AuthUser, Page, Role, Question, Answer, QuizResult


#Creating the model serializer for auth user model
class UserSerializer(serializers.ModelSerializer):

    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = AuthUser
        fields = ['id', 'username','email', 'password', 'auth_user_type','role', 'role_name']
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
        instance.role = validated_data.get('role', instance.role)

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

        
# Creating the question serializer
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question', 'selected_order']


# Creating the answer serializer
class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


# Creating the answer sending serializer (for web)
class AnswerSendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answer', 'mark']


# Creating the question sending serializer (for web app)
class QuestionSendingSerializer(serializers.ModelSerializer):
    answers = AnswerSendingSerializer(many = True, read_only = True, source = 'answer_set')

    class Meta:
        model = Question
        fields = ['id', 'question', 'answers']

class QuizResultSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    age = serializers.CharField(source='user.age', read_only=True)
    class Meta:
        model = QuizResult
        fields = ['id', 'user', 'questions', 'score', 'dp_level', 'no_of_days', 'conclusion', 'counselor_or_not', 'date', 'time','is_seen', 'user_name', 'age']


class AppointmentSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='quiz_result.user.first_name', read_only=True)
    last_name = serializers.CharField(source='quiz_result.user.last_name', read_only=True)
    dp_level = serializers.CharField(source='quiz_result.dp_level', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'first_name',
            'last_name',
            'quiz_result_id',
            'admin_id',
            'requested_date',
            'is_checked',
            'scheduled_date',
            'scheduled_time_period',
            'response_description',
            'dp_level'  
        ]


class UserAppointments(serializers.ModelSerializer):
    first_name = serializers.CharField(source='quiz_result.user.first_name', read_only=True)
    last_name = serializers.CharField(source='quiz_result.user.last_name', read_only=True)
    age = serializers.CharField(source='quiz_result.user.age', read_only=True)
    score = serializers.CharField(source='quiz_result.score', read_only=True)
    dp_level = serializers.CharField(source='quiz_result.dp_level', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'first_name',
            'last_name',
            'age',
            'quiz_result_id',
            'admin_id',
            'requested_date',
            'is_checked',
            'scheduled_date',
            'scheduled_time_period',
            'response_description',
            'dp_level',
            'score' 
        ]



