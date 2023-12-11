
from datetime import datetime, timedelta
import string
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
import jwt
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tsd_main_app.models import AuthUser, Question, QuizResult, User
from tsd_main_app.serializers import UserLoginSerializer, AuthUserSerializer, UserSerializer,QuestionSendingSerializer , QuizResultSerializer, QuizQandASerializer, QuizResultSendingSerializer


# Creating the view to register the user
class UserRegisterView(APIView):
    def post(self, request):

        #Getting both data sets for the two models
        auth_user_data = request.data.get('auth_user', {})
        user_data = request.data.get('user', {})

        #Putting auth_user_type = user in the auth_user_data set
        auth_user_data['auth_user_type'] = 'user'
        
        # Putting the data set inside the auth user serializer
        auth_user_serializer = AuthUserSerializer(data = auth_user_data)

        #Checking if the auth_user_serializer is valid
        if(auth_user_serializer.is_valid()):
            #Create the record
            auth_user_instance = auth_user_serializer.save()
        else:
            #Return the relavant errors
            print(auth_user_serializer.errors)
            return JsonResponse({'status': 'Data is not valid','errors': auth_user_serializer.errors}, status=400)
        
        #Putting the auth_user_id in the user data set
        user_data['auth_user'] = auth_user_instance.id

        # Putting the user data into the user serializer
        user_serializer = UserSerializer(data = user_data)

        #Checking the data validation
        if(user_serializer.is_valid()):

            # Creating the new records in the tables
            user_serializer.save()

            # Returning a success response to the fluttter terminal
            return JsonResponse({'status': 'success'}, status=201)
        else:
            # If the data is not valid, sending the relavant error to the frontend and delete the created auth user record
            auth_user_instance.delete()
            return JsonResponse({'status': 'Data is not valid','errors': user_serializer.errors}, status=400)
    


# Creating the view to login the user
class UserLoginView(APIView):
    def post(self,request):

        # Putting the login information to the serailizer
        user_login_serializer = UserLoginSerializer(data = request.data)

        #Checking if the data is valid
        if(user_login_serializer.is_valid()):
            username = user_login_serializer.validated_data['username']
            password = user_login_serializer.validated_data['password']

            # Authenticating the user
            authuser = authenticate(request, username=username, password=password)
        
            # Displaying results in the  Django terminal
            print(f'username: {username}, Password: {password}')
            print(f'Authentication Result: {authuser}')
        
            # If there is a user,
            if authuser is not None:
                if authuser.auth_user_type == 'user':
                    # create a JWT token
                    token = generate_jwt_token(authuser)

                    # create and send a login response including the token
                    login(request, authuser)
                    return JsonResponse({'status': 'success', 'token': token}, status=200)
                else:
                    return JsonResponse({'error': 'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
            # If there is not, 
            else:
                # create and send an error response
                return JsonResponse({'error': 'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
            
        # If the data is not valid
        else:
            return JsonResponse({'status': 'Data is not valid'}, status=400)
        


# Function that creates a JWT token
def generate_jwt_token(authuser):
    # Set the expiration time (e.g., 1 hour from now)
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    # Creating the payload
    payload = {
        'username' : authuser.username,
        'auth_user_id' : authuser.id,
        'auth_user_type': authuser.auth_user_type,
        'exp': expiration_time,
    }

    # generate the JWT token
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')

    # Returning the token
    return token



# creating the view for sending the questions and answers
class QuizSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the auth user type is user
        if request.user.auth_user_type == 'user':

            print(request.user.auth_user_type)

            #Getting the questions from the database
            questions = Question.objects.exclude(selected_order = 0).order_by('selected_order')
            quiz_sending_serializer = QuestionSendingSerializer(questions, many=True)

            #Sending the data to the frontend as a Json Response
            return JsonResponse({'questions_and_answers' : quiz_sending_serializer.data}, status=200)

        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)




#Creating the view to store the quiz result data, quiz q and a data in the relavant tables
class QuizResultStoringView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the auth user type is user
        if request.user.auth_user_type == 'user':

            # Getting the user_id through the auth_user_id
            user = User.objects.get(auth_user = request.user.id)
            print(user)

            user_id = user.id

            #Adding the user id to the data set
            quiz_result_data = request.data.get('quiz_result_data', {})
            quiz_q_and_a_data = request.data.get('quiz_q_and_a_data', {})

            quiz_result_data['user'] = user_id

            #Putting the data sets to the serializers and validating them, saving them
            quiz_result_serializer = QuizResultSerializer(data = quiz_result_data)

            #Checking if the quiz result serializer is valid
            if quiz_result_serializer.is_valid():

                #saving the quiz result data
                quiz_result_instance = quiz_result_serializer.save()

                #Adding quiz result id to every data map of the quiz q and a data
                for quiz_q_and_a_item in quiz_q_and_a_data:
                    quiz_q_and_a_item['quiz_result'] = quiz_result_instance.id

                #putting the data to the quiz q and a serializer
                quiz_q_and_a_serializer = QuizQandASerializer(data=quiz_q_and_a_data, many=True)

                #Checking if the quiz q and a serializer is valid
                if quiz_q_and_a_serializer.is_valid():

                    #saving the quiz questions and answers
                    quiz_q_and_a_serializer.save()

                    #returning the response that contains the quiz result id
                    return JsonResponse({'Status': 'Data Submitted submitted successfully', 'quiz_result_id': quiz_result_instance.id}, status=201)
                
                else:
                    #Deleting the created quiz result record
                    quiz_result_instance.delete()
                    return JsonResponse({'errors': quiz_q_and_a_serializer.errors},status=400)
                
            else:
                return JsonResponse({'errors':quiz_result_serializer.errors},status=400)
        
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)




#Creating the view to send the requested quiz result data
class QuizResultSendingView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Check if the auth user type is user
        if request.user.auth_user_type == 'user':

            #Putting the data to the serializer
            quiz_result_sending_serializer = QuizResultSendingSerializer(data = request.data)

            #Checking if the serializer is valid
            if quiz_result_sending_serializer.is_valid():

                #Get the quiz result data into a variable
                sending_quiz_result = QuizResult.objects.get(id = quiz_result_sending_serializer.validated_data['quiz_result_id'])

                # Check if a quiz result was found
                if sending_quiz_result is not None:
                    # Create the map with the quiz result data
                    quiz_result_data = {
                        'date': sending_quiz_result.date,
                        'time': sending_quiz_result.time,
                        'score': sending_quiz_result.score,
                        'dp_level': sending_quiz_result.dp_level,
                        'conclusion': sending_quiz_result.conclusion,
                        'counselor_or_not': sending_quiz_result.counselor_or_not,
                    }
                    print(quiz_result_data)
                    #Send the quiz result data to the frontend as a Json Response
                    return JsonResponse(quiz_result_data,status = 200)
                
                else:
                    print("No result data found")
                    return JsonResponse({'error':'no result data found'}, status=400)
                
            else:
                return JsonResponse(quiz_result_sending_serializer.errors, status = 400)
            
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)








