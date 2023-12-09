
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
from tsd_main_app.models import AuthUser, Question
from tsd_main_app.serializers import UserLoginSerializer, AuthUserSerializer, UserSerializer,QuestionSendingSerializer


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















#Creating the view to store the data in the result table
#@api_view(['POST'])
#@permission_classes([IsAuthenticated])
#def store_result(request):
    #Getting the data in the request
    ##data = request.data

    #Adding the user_id to the data, by getting user_id from the user object we created within the jwt authentication
    #data['user'] = request.user.id

    #Adding data to the serializer
    #result_serializer = ResultSerializer(data = data)

    #Checking if the serislizer is valid
    #if result_serializer.is_valid():

        #Creating the database record
        #result_serializer.save()
        
        #return JsonResponse({'result':'Results has been submitted successfully'}, status=201)
    
    #else:
        #return JsonResponse(result_serializer.errors, status = 400)
    
    


#Creating the view to send the requested result data
#@api_view(['POST'])
#@permission_classes([IsAuthenticated])
#def view_result(request):

    #Getting the user id of the user through the authentication
    #user_id = request.user.id

    #Putting the date and time to the serializer
    #view_result_serializer = ViewResultSerializer(data = request.data)

    #Checking if the serializer is valid
    #if view_result_serializer.is_valid():

        ##Getting the data and time to variables
        #received_date = view_result_serializer.validated_data['date']
        #received_time = view_result_serializer.validated_data['time']

        #Get the result data into a variable
        #sending_result = Result.objects.filter(user=user_id,date = received_date, time = received_time).order_by('id').first()

        # Check if a result was found
        #if sending_result is not None:
            # Create the map with the result data
            #result_data = {
                #'date': sending_result.date,
                #'time': sending_result.time,
                #'test_score': sending_result.test_score,
                #'depression_level': sending_result.depression_level,
                #'conclusion': sending_result.conclusion
            #}
            #print(result_data)
            #Send the result data to the frontend as a Json Response
            #return JsonResponse(result_data,status = 200)
        #else:
            ##print("No result data found")
            #return JsonResponse({'error':'no result data found'}, status=400)
    #else:
        #return JsonResponse(view_result_serializer.errors, status = 400)








