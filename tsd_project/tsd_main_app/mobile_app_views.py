
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from tsd_main_app.models import Admin, Appointment, AuthUser, PrivateQuestions, Question, QuizResult, Role, Patient
from tsd_main_app.mobile_app_serializers import AppointmentSerializer, PatientLoginSerializer, AuthUserSerializer, PatientSerializer, PrivateQuestionsSerializer,QuestionSendingSerializer , QuizResultSerializer, QuizQandASerializer, QuizResultSendingSerializer, PreviousQuizResultSendingSerializer


# Creating the view to register the patient
class PatientRegisterView(APIView):
    def post(self, request):

        #Getting both data sets for the two models
        auth_user_data = request.data.get('auth_user', {})
        patient_data = request.data.get('patient', {})

        #Putting auth_user_type = patient in the auth_user_data set
        auth_user_data['auth_user_type'] = 'patient'

        try:
            #Getting the role id of the patient from the role model and adding it to the data list
            patient_role = Role.objects.get(name = "Patient")
            patient_role_id = patient_role.id
            auth_user_data['role'] = patient_role_id

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
            
            #Putting the auth_user_id in the patient data set
            patient_data['auth_user'] = auth_user_instance.id

            # Putting the patient data into the patient serializer
            patient_serializer = PatientSerializer(data = patient_data)

            #Checking the data validation
            if(patient_serializer.is_valid()):

                # Creating the new records in the tables
                patient_serializer.save()

                # Returning a success response to the fluttter terminal
                return JsonResponse({'status': 'success'}, status=201)
            else:
                # If the data is not valid, sending the relavant error to the frontend and delete the created auth user record
                auth_user_instance.delete()
                return JsonResponse({'status': 'Data is not valid','errors': patient_serializer.errors}, status=400)
            
        except Role.DoesNotExist:
            return JsonResponse({'Not Found':'No role object found'}, status = 400)
    


# Creating the view to login the patient
class PatientLoginView(APIView):
    def post(self,request):

        # Putting the login information to the serailizer
        patient_login_serializer = PatientLoginSerializer(data = request.data)

        #Checking if the data is valid
        if(patient_login_serializer.is_valid()):
            username = patient_login_serializer.validated_data['username']
            password = patient_login_serializer.validated_data['password']

            # Authenticating the user
            authuser = authenticate(request, username=username, password=password)
        
            # Displaying results in the  Django terminal
            print(f'username: {username}, Password: {password}')
            print(f'Authentication Result: {authuser}')
        
            # If there is a user,
            if authuser is not None:
                if authuser.auth_user_type == 'patient':
                    # create a JWT access token and a refresh token using simple jwt
                    tokens = generate_jwt_token(authuser)
                    access_token = tokens['access_token']
                    refresh_token = tokens['refresh_token']

                    print(access_token)
                    print(refresh_token)

                    # create and send a login response including the access token and the refresh token
                    login(request, authuser)
                    return JsonResponse({'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token}, status=200)
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
    access_token = refresh_token.access_token

    # Returning the access token and the refresh token
    tokens = {'access_token': str(access_token), 'refresh_token': str(refresh_token)}
    return tokens


#Regenerate accessToken view
class RegenerateAccessToken(APIView):

    def post(self,request):

        refresh_token = request.data.get('refresh_token')

        try:
            access_token = RefreshToken(refresh_token).access_token

            return JsonResponse({'success': 'access token generated', 'access_token': str(access_token)}, status=201)
        
        except TokenError:
            return JsonResponse({'error': 'Invalid tokens or expired'}, status=400)
    


#Patient tokens blacklisting view
class BlacklistTokensView(APIView):
    
    def post(self,request):

        refresh_token = request.data.get('refresh_token')
        access_token = request.data.get('access_token')

        try:
            RefreshToken(refresh_token).blacklist()

            return JsonResponse({'success': 'Tokens blacklisted'}, status=201)
        
        except TokenError:
            return JsonResponse({'error': 'Invalid tokens or expired'}, status=400)
        


#Account deleting view
class DeleteAccountView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        # Check if the auth user type is patient
        if request.user.auth_user_type == 'patient':

            try:
                auth_user_object = AuthUser.objects.get(id = request.user.id)

                auth_user_object.delete()

                return JsonResponse({'success': 'Account deleted successfully'}, status=201)

            except AuthUser.DoesNotExist:
                return JsonResponse({'Not Found':'No auth user object found'}, status = 400)

        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
    
    


# creating the view for sending the questions and answers
class QuizSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if the auth user type is patient
        if request.user.auth_user_type == 'patient':

            print(request.user.auth_user_type)

            #Getting the questions from the database
            questions = Question.objects.exclude(selected_order = 0).order_by('selected_order')

            if questions:

                #Get one question and check if the is_updating true
                check_question = Question.objects.exclude(selected_order=0).first()
                print(check_question)

                if(check_question.is_updating == False):
                
                    quiz_sending_serializer = QuestionSendingSerializer(questions, many=True)
                    print(check_question.last_updated_timestamp)

                    #Sending the data and the last updated timestamp to the frontend as a Json Response
                    return JsonResponse({'questions_and_answers' : quiz_sending_serializer.data, 'last_updated_timestamp': str(check_question.last_updated_timestamp)}, status=200)
                
                #If the is_updating is true send to the frontend, that questions are updating
                else:
                    return JsonResponse({'quiz_updating': 'The quiz is in maintenance. Please try again later'}, status = 400)
            
            #If there are no questions send to the frontend, that questions are updating
            else:
                return JsonResponse({'quiz_updating': 'The quiz is in maintenance. Please try again later'}, status = 400)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)




#Creating the view to store the quiz result data, quiz q and a data in the relavant tables
class QuizResultStoringView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if the auth user type is patient
        if request.user.auth_user_type == 'patient':

            try:
                # Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                #Get a question instance and check the is_updating status
                check_question = Question.objects.first()

                if check_question:

                    if(check_question.is_updating == False):

                        print(request.data.get('last_updated_timestamp'))
                        print(check_question.last_updated_timestamp)
                        
                        #Check if the quiz is updated within the time that the patient doing it
                        if(str(check_question.last_updated_timestamp) == request.data.get('last_updated_timestamp')):

                            #Adding the patient id to the data set
                            quiz_result_data = request.data.get('quiz_result_data', {})
                            quiz_q_and_a_data = request.data.get('quiz_q_and_a_data', {})

                            quiz_result_data['patient'] = patient_id

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
                            return JsonResponse({'quiz_updated': 'Quiz has been updated'}, status=400)
                    else:
                        return JsonResponse({'quiz_updating': 'Quiz is under maintenance'}, status=400)
                else:
                    return JsonResponse({'quiz_updating': 'Quiz is under maintenance'}, status=400)
                
            except Patient.DoesNotExist:
                return JsonResponse({'Not Found':'No patient object found'}, status = 400)
        
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)




#Creating the view to send the requested quiz result data
class QuizResultSendingView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Check if the auth user type is patient
        if request.user.auth_user_type == 'patient':

            #Putting the data to the serializer
            quiz_result_sending_serializer = QuizResultSendingSerializer(data = request.data)

            #Checking if the serializer is valid
            if quiz_result_sending_serializer.is_valid():

                try:

                    #Get the quiz result data into a variable
                    sending_quiz_result = QuizResult.objects.get(id = quiz_result_sending_serializer.validated_data['quiz_result_id'])

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
                    
                except QuizResult.DoesNotExist:
                    return JsonResponse({'Not Found':'No quiz result object found'}, status=400)
                
            else:
                return JsonResponse(quiz_result_sending_serializer.errors, status = 400)
            
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send the previous quiz result data
class PreviousQuizResultSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        #Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:

                # Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                #Getting the relavant data set from the database
                previous_quiz_results = QuizResult.objects.filter(patient = patient_id)

                previous_quiz_result_serializer = PreviousQuizResultSendingSerializer(previous_quiz_results, many = True)

                #Sending the data to the frontend as a Json Response
                return JsonResponse({'previous_quiz_results' : previous_quiz_result_serializer.data}, status=200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'Not Found':'No Patient object found'}, status=400)
        
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send the Patient personal details
class PatientPersonalDetailsSendingView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        #Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                #Getting the patient object from the databse
                patient_instance = Patient.objects.get(id = patient_id)

                print(patient_instance.age)

                #Putting the data to serailizer and then sending them as a json response
                patient_personal_details_sending_serializer = PatientSerializer(patient_instance)

                print(patient_personal_details_sending_serializer.data)

                return JsonResponse({'patient_personal_details':patient_personal_details_sending_serializer.data},status = 200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'Not Found':'No Patient object found'}, status=400)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)



#Creating the view to update patient personal details
class PatientPersonalDetailsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        #Checking the auth user type
        if request.user.auth_user_type == 'patient':
            
            try:

                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                #Get the patient instance for that id
                patient_instance = Patient.objects.get(id=patient_id)

                #Updating the data through the serializer
                patient_personal_details_updating_serializer = PatientSerializer(patient_instance, data = request.data, partial=True)

                if patient_personal_details_updating_serializer.is_valid():

                    patient_personal_details_updating_serializer.save()

                    return JsonResponse({'Suceess': 'Data updated successfully'}, status=201)

                else:
                    return JsonResponse({'Error': patient_personal_details_updating_serializer.errors}, status=400)
                
            except Patient.DoesNotExist:
                return JsonResponse({'Not Found':'No patient object found'}, status=400)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send the patient auth user details
class PatientAuthUserDetailsSendingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'patient':

            #Getting the auth_user_id to a variable
            auth_user_id = request.user.id

            try:

                #Getting the object of that auth user id
                auth_user_object = AuthUser.objects.get(id = auth_user_id)

                #Putting it to the serializer and sending the serializer data to the frontend
                patient_auth_user_details_sending_serializer = AuthUserSerializer(auth_user_object)

                return JsonResponse({'patient_auth_user_details': patient_auth_user_details_sending_serializer.data}, status=200)
            
            except AuthUser.DoesNotExist:
                return JsonResponse({'Not Found':'No Auth user object found'}, status = 400)
        else:
            return JsonResponse({'error': 'You does not have permission to access this content'}, status=400)
        

#Creating the view to update patient auth user details
class PatientAuthUserDetailsUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'patient':

            #Getting the current password and new updating data to variables
            current_password = request.data.get('current_password')
            print(current_password)

            patient_auth_user_data = request.data.get('patient_auth_user_details', {})
            print(patient_auth_user_data)

            #Validating the current password
            patient_auth_user = authenticate(request, username= request.user.username, password = current_password)
            print(patient_auth_user)

            if patient_auth_user is not None:
                
                #Updating the auth user details
                patient_auth_user_details_updating_serializer = AuthUserSerializer(patient_auth_user, data = patient_auth_user_data, partial=True)

                if patient_auth_user_details_updating_serializer.is_valid():

                    patient_auth_user_details_updating_serializer.save()

                    return JsonResponse({'Sucess': 'Data updated successfully'}, status=201)
                else:
                    return JsonResponse({'errors': patient_auth_user_details_updating_serializer.errors}, status=400)
                
            else:
                return JsonResponse({'error': 'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        


#Creating the view to send all the counselor details to the mobile application
class SendCounselorDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        #Checking the auth user type
        if request.user.auth_user_type == 'patient':

            #create a list to store the counselor deatils
            counselor_details = []

            try:

                #Check if there is a admin role named Counselor
                counselor_role_object = Role.objects.get(name = "Counselor")

                #Get the counselor role id into a variable
                counselor_role_id = counselor_role_object.id

                #Get all the objects realated to that role id from the auth user table
                counselors = AuthUser.objects.filter(role = counselor_role_id)

                #if there are at least one instance of counselors
                if counselors:

                    #generate the counselor details for every object
                    for counselor in counselors:

                        try:
                            #Get the admin details related to the counselor
                            admin_object = Admin.objects.get(auth_user = counselor.id)

                            if(admin_object.first_name is not None and admin_object.last_name is not None and admin_object.location is not None and admin_object.mobile_number is not None and admin_object.website is not None and admin_object.profile_image is not None):

                                print(admin_object.profile_image)

                                counselor_details.append({
                                    'auth_user_id': counselor.id,
                                    'admin_id': admin_object.id,
                                    'email':counselor.username,
                                    'first_name': admin_object.first_name,
                                    'last_name':admin_object.last_name,
                                    'location': admin_object.location,
                                    'mobile_number':admin_object.mobile_number,
                                    'website':admin_object.website,
                                    'profile_image': str(admin_object.profile_image),
                                })
                        except Admin.DoesNotExist:
                            return JsonResponse({'Not Found':'Admin object not found'}, status=400)
                    
                    #Send the counselor data list to the frontend
                    return JsonResponse({'counselor_details': counselor_details}, status=200)
                
                #If there are no counselors available
                else:
                    return JsonResponse({'counselor_details': counselor_details}, status=200)
            
            #If there is no admin role named Counselor, send the empty list to the frontend
            except Role.DoesNotExist:
                return JsonResponse({'counselor_details': counselor_details}, status=200)
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        


# Creating the view to store the appointment details
class MakeAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:

                #Check if an counselor is available with that id
                requested_counselor = Admin.objects.get(id = request.data.get('admin'))

                print(requested_counselor.id)
            
                #get the data set and add the accepted = false to it
                appointment_data = request.data

                appointment_data['is_checked'] = False

                #Putting the data to the serializer
                appointment_making_serializer = AppointmentSerializer(data= appointment_data)

                #Checking the serializer is valid
                if appointment_making_serializer.is_valid():

                    #Saving the serializer
                    appointment_making_serializer.save()

                    return JsonResponse({'status' : 'success'}, status=201)
                else:
                    return JsonResponse({'Errors': appointment_making_serializer.errors}, status=400)
                
            except Admin.DoesNotExist:
                return JsonResponse({'counselor_deleted': 'counselor is not available' }, status=400)

        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        



# Creating the view to check whether there is any on going appointments
class checkOngoingAppointmentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            # get all the appointments related to the quiz result id and admin id
            appointments = Appointment.objects.filter(quiz_result = request.data.get('quiz_result'), admin = request.data.get('admin'))

            #Check if there is at least one object
            if appointments:

                return JsonResponse({'can_make_appointment' : 'false'}, status=201)
            
            #If there is no appointments, send true
            else:
                return JsonResponse({'can_make_appointment' : 'true'}, status=201)
            
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

#Appointment list sending view
class AppointmentListSendingView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try: 
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                #Create a list to store the data that must be send to the frontend
                appointment_list = []

                #Getting all the quiz results related to that patient id
                quiz_results = QuizResult.objects.filter(patient = patient_id)

                if quiz_results:

                    #For each quiz result get all the appointments related to that
                    for quiz_result in quiz_results:

                        appointments = Appointment.objects.filter(quiz_result = quiz_result.id)

                        if appointments:

                            #For each of these appointments get the appointments that are scheduled
                            for appointment in appointments:

                                if(appointment.scheduled_date is not None and appointment.scheduled_time_period is not None and appointment.response_description is not None):

                                    try:

                                        #Get the admin object related to the appointment
                                        admin = Admin.objects.get(id = appointment.admin.id)

                                        if(appointment.is_patient_viewed == True):
                                            is_patient_viewed = 1
                                        else:
                                            is_patient_viewed = 0

                                        appointment_list.append({
                                            'appointment_id': appointment.id,
                                            'appointment_date': appointment.scheduled_date,
                                            'appointment_time': appointment.scheduled_time_period,
                                            'counselor_first_name': admin.first_name,
                                            'counselor_last_name': admin.last_name,
                                            'appointment_location': admin.location,
                                            'response_description': appointment.response_description,
                                            'is_patient_viewed': is_patient_viewed,
                                            'profile_image': str(admin.profile_image),
                                        })
                                    
                                    except Admin.DoesNotExist:
                                        return JsonResponse({'error': 'admin is not available' }, status=400)
                        
                        else:
                            continue

                    appointment_list.sort(key=lambda x:x['appointment_id'])
                    return JsonResponse({'appointment_list' : appointment_list}, status = 200)
                
                else:
                    return JsonResponse({'appointment_list' : appointment_list}, status = 200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'patient is not available' }, status=400)
                    
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)


#View that makes the appointment is_patient_viewed attribute true
class MakeAppointmentIsPatientViewedTrueView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            appointment_id = request.data.get('appointment_id')

            try:
                appointment_object = Appointment.objects.get(id = appointment_id)

                appointment_object.is_patient_viewed = True

                appointment_object.save()

                return JsonResponse({'status': 'success'}, status=201)

            except Appointment.DoesNotExist:
                return JsonResponse({'error': 'appointment is not available' }, status=400)

        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

#View to send the appointments notifications amount
class SendAppointmentsNotificationsAmountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try: 
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                appointmentsNotificationsAmount = 0

                #Getting all the quiz results related to that patient id
                quiz_results = QuizResult.objects.filter(patient = patient_id)

                if quiz_results:

                    #For each quiz result get all the appointments related to that
                    for quiz_result in quiz_results:

                        appointments = Appointment.objects.filter(quiz_result = quiz_result.id)

                        if appointments:

                            #For each of these appointments get the appointments that are scheduled
                            for appointment in appointments:

                                if(appointment.scheduled_date is not None and appointment.scheduled_time_period is not None and appointment.response_description is not None and appointment.is_patient_viewed == False):

                                    appointmentsNotificationsAmount += 1
                        
                        else:
                            continue
                        
                    return JsonResponse({'appointments_notifications_amount' : str(appointmentsNotificationsAmount)}, status = 200)
                
                else:
                    return JsonResponse({'appointments_notifications_amount' : str(appointmentsNotificationsAmount)}, status = 200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'patient is not available' }, status=400)
                    
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

# Storing the private question view
class StorePrivateQuestionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                private_question_data = request.data

                private_question_data['private_answer'] = "--"
                private_question_data['patient'] = patient_id

                private_question_serializer = PrivateQuestionsSerializer(data = private_question_data)

                if private_question_serializer.is_valid():

                    private_question_serializer.save()

                    return JsonResponse({'success':'private question submitted successfully'}, status=201)
                
                else:
                    return JsonResponse({'errors':private_question_serializer.errors}, status=400)
            
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'patient is not available' }, status=400)

        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

# Send the private questions view
class SendPrivateQuestionsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                private_questions_list = []

                private_question_objects = PrivateQuestions.objects.filter(patient = patient_id)

                if private_question_objects:

                    for private_question_object in private_question_objects:

                        if(private_question_object.is_patient_viewed == True):
                            is_patient_viewed = 1
                        else:
                            is_patient_viewed = 0

                        private_questions_list.append({
                            'private_question_id': private_question_object.id,
                            'private_question': private_question_object.private_question,
                            'private_answer': private_question_object.private_answer,
                            'asked_date': private_question_object.asked_date,
                            'asked_time': private_question_object.asked_time,
                            'is_patient_viewed': is_patient_viewed,
                            'counselor_first_name': private_question_object.admin.first_name,
                            'counselor_last_name': private_question_object.admin.last_name,
                        })
                    
                    return JsonResponse({'private_questions_and_answers': private_questions_list}, status = 200)
                
                else:
                    return JsonResponse({'private_questions_and_answers': private_questions_list}, status = 200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'patient is not available' }, status=400)
        
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

#View that makes the private question is_patient_viewed attribute true
class MakePrivateQuestionIsPatientViewedTrueView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            private_question_id = request.data.get('private_question_id')

            try:
                private_question_object = PrivateQuestions.objects.get(id = private_question_id)

                private_question_object.is_patient_viewed = True

                private_question_object.save()

                return JsonResponse({'status': 'success'}, status=201)

            except PrivateQuestions.DoesNotExist:
                return JsonResponse({'error': 'private question is not available' }, status=400)

        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)
        

#View to send the private questions notifications amount
class SendPrivateQuestionsNotificationsAmountView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        # Checking the auth user type
        if request.user.auth_user_type == 'patient':

            try:
                #Getting the patient_id through the auth_user_id
                patient = Patient.objects.get(auth_user = request.user.id)
                print(patient)

                patient_id = patient.id

                privateQuestionsNotificationsAmount = 0

                private_question_objects = PrivateQuestions.objects.filter(patient = patient_id)

                if private_question_objects:

                    for private_question_object in private_question_objects:

                        if(private_question_object.is_patient_viewed == False):
                            privateQuestionsNotificationsAmount += 1
                
                return JsonResponse({'private_questions_notifications_amount': str(privateQuestionsNotificationsAmount)}, status = 200)
            
            except Patient.DoesNotExist:
                return JsonResponse({'error': 'patient is not available' }, status=400)
                    
        else:
            return JsonResponse({'errors': 'You does not have permission to access this content'}, status=400)








