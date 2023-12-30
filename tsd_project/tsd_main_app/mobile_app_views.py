
from datetime import datetime, timedelta
import string
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from tsd_main_app.models import Admin, Appointment, AuthUser, Question, QuizResult, Role, User
from tsd_main_app.mobile_app_serializers import AppointmentSerializer, UserLoginSerializer, AuthUserSerializer, UserSerializer,QuestionSendingSerializer , QuizResultSerializer, QuizQandASerializer, QuizResultSendingSerializer, PreviousQuizResultSendingSerializer


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
                    # create a JWT access token using simple jwt
                    access_token = generate_jwt_token(authuser)

                    # create and send a login response including the access token
                    login(request, authuser)
                    return JsonResponse({'status': 'success', 'access_token': access_token}, status=200)
                else:
                    return JsonResponse({'error': 'Invalid Credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
            # If there is not, 
            else:
                # create and send an error response
                return JsonResponse({'error': 'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
            
        # If the data is not valid
        else:
            return JsonResponse({'status': 'Data is not valid'}, status=400)
        


# Function that creates a JWT token using simple jwt
def generate_jwt_token(authuser):

    #Generate a refresh token
    refresh_token = RefreshToken.for_user(authuser)

    #Generate an access token for that refresh token
    access_token = str(refresh_token.access_token)

    # Returning the access token
    return access_token



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
        


#Creating the view to send the previous quiz result data
class PreviousQuizResultSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #Checking the auth user type
        if request.user.auth_user_type == 'user':

            # Getting the user_id through the auth_user_id
            user = User.objects.get(auth_user = request.user.id)
            print(user)

            user_id = user.id

            #Getting the relavant data set from the database
            previous_quiz_results = QuizResult.objects.filter(user = user_id)

            previous_quiz_result_serializer = PreviousQuizResultSendingSerializer(previous_quiz_results, many = True)

            #Sending the data to the frontend as a Json Response
            return JsonResponse({'previous_quiz_results' : previous_quiz_result_serializer.data}, status=200)
        
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send the user personal details
class UserPersonalDetailsSendingView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        #Checking the auth user type
        if request.user.auth_user_type == 'user':

            #Getting the user_id through the auth_user_id
            user = User.objects.get(auth_user = request.user.id)
            print(user)

            user_id = user.id

            #Getting the user object from the databse
            user_instance = User.objects.get(id = user_id)

            print(user_instance.age)

            #Putting the data to serailizer and then sending them as a json response
            user_personal_details_sending_serializer = UserSerializer(user_instance)

            print(user_personal_details_sending_serializer.data)

            return JsonResponse({'user_personal_details':user_personal_details_sending_serializer.data},status = 200)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)



#Creating the view to update user personal details
class UserPersonalDetailsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        #Checking the auth user type
        if request.user.auth_user_type == 'user':
            
            #Getting the user_id through the auth_user_id
            user = User.objects.get(auth_user = request.user.id)
            print(user)

            user_id = user.id

            #Get the user instance for that id
            user_instance = User.objects.get(id=user_id)

            #Updating the data through the serializer
            user_personal_details_updating_serializer = UserSerializer(user_instance, data = request.data, partial=True)

            if user_personal_details_updating_serializer.is_valid():

                user_personal_details_updating_serializer.save()

                return JsonResponse({'Suceess': 'Data updated successfully'}, status=201)

            else:
                return JsonResponse({'Error': user_personal_details_updating_serializer.errors}, status=400)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send the user auth user details
class UserAuthUserDetailsSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'user':

            #Getting the auth_user_id to a variable
            auth_user_id = request.user.id

            #Getting the object of that auth user id
            auth_user_object = AuthUser.objects.get(id = auth_user_id)

            #Putting it to the serializer and sending the serializer data to the frontend
            user_auth_user_details_sending_serializer = AuthUserSerializer(auth_user_object)

            return JsonResponse({'user_auth_user_details': user_auth_user_details_sending_serializer.data}, status=200)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        

#Creating the view to update user auth user details
class UserAuthUserDetailsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'user':

            #Getting the current password and new updating data to variables
            current_password = request.data.get('current_password')

            user_auth_user_data = request.data.get('user_auth_user_details', {})

            #Validating the current password
            user_auth_user = authenticate(request, username= request.user.username, password = current_password)

            if user_auth_user is not None:
                
                #Updating the auth user details
                user_auth_user_details_updating_serializer = AuthUserSerializer(user_auth_user, data = user_auth_user_data, partial=True)

                if user_auth_user_details_updating_serializer.is_valid():

                    user_auth_user_details_updating_serializer.save()

                    return JsonResponse({'Sucess': 'Data updated successfully'}, status=201)
                else:
                    return JsonResponse({'errors': user_auth_user_details_updating_serializer.errors}, status=400)
                
            else:
                return JsonResponse({'error': 'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send all the counselor details to the mobile application
class SendCounselorDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'user':

            #create a list to store the counselor deatils
            counselor_details = []

            #Check if there is a admin role named Counselor
            counselor_role_object = Role.objects.get(name = "Counselor")

            if counselor_role_object is not None:

                #Get the counselor role id into a variable
                counselor_role_id = counselor_role_object.id

                #Get all the objects realated to that role id from the auth user table
                counselors = AuthUser.objects.filter(role = counselor_role_id)

                #if there are at least one instance of counselors
                if counselors:

                    #generate the counselor details for every object
                    for counselor in counselors:

                        #Get the admin details related to the counselor
                        admin_object = Admin.objects.get(auth_user = counselor.id)

                        #Adding the admin_details and the username (as the email address) to the declared list
                        if admin_object is not None:

                            if(admin_object.first_name is not None and admin_object.last_name is not None and admin_object.location is not None and admin_object.mobile_number is not None and admin_object.website is not None):

                                counselor_details.append({
                                    'auth_user_id': counselor.id,
                                    'admin_id': admin_object.id,
                                    'email':counselor.username,
                                    'first_name': admin_object.first_name,
                                    'last_name':admin_object.last_name,
                                    'location': admin_object.location,
                                    'mobile_number':admin_object.mobile_number,
                                    'website':admin_object.website,
                                })
                    
                    #Send the counselor data list to the frontend
                    return JsonResponse({'counselor_details': counselor_details}, status=200)
                
                #If there are no counselors available
                else:
                    return JsonResponse({'counselor_details': counselor_details}, status=200)
            
            #If there is no admin role named Counselor, send the empty list to the frontend
            else:
                return JsonResponse({'counselor_details': counselor_details}, status=200)
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        


# Creating the view to store the appointment details
class MakeAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Checking the auth user type
        if request.user.auth_user_type == 'user':
        
            #get the data set and add the accepted = false to it
            appointment_data = request.data

            appointment_data['accepted'] = False

            #Putting the data to the serializer
            appointment_making_serializer = AppointmentSerializer(data= appointment_data)

            #Checking the serializer is valid
            if appointment_making_serializer.is_valid():

                #Saving the serializer
                appointment_making_serializer.save()

                return JsonResponse({'status' : 'success'}, status=201)
            else:
                return JsonResponse({'Errors': appointment_making_serializer.errors}, status=400)

        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        



# Creating the view to check whether there is any on going appointments
class checkOngoingAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Checking the auth user type
        if request.user.auth_user_type == 'user':

            # get all the appointments related to the quiz result id and admin id
            appointments = Appointment.objects.filter(quiz_result = request.data.get('quiz_result'), admin = request.data.get('admin'))

            #Check if there is at least one object
            if appointments:

                #Check whether there is a appointment which has accepted = False
                for appointment in appointments:

                    if(appointment.accepted == False):

                        return JsonResponse({'can_make_appointment' : 'false'}, status=201)
                
                #If there is no appointments which has accepted = False, send true
                return JsonResponse({'can_make_appointment' : 'true'}, status=201)
            
            #If there is no appointments, send true
            else:
                return JsonResponse({'can_make_appointment' : 'true'}, status=201)
            
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)








