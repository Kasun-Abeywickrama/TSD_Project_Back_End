from random import randint
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from django.conf import settings
from .models import Admin, Appointment, AuthUser, Page, PrivateQuestions, QuizResult, Role, RolePage, Question, Answer, QuizQandA
from .web_app_serializers import AdminSerializer, AppointmentSerializer, PageSerializer, PrivateQuestionsSerializer, PrivateQuestionsUpdateSerializer, QuizResultSerializer, RolePageSerializer, RoleSerializer, UpdateCurrentUserSerializer, UserAppointments, UserSerializer, QuestionSerializer, AnswerSerializer, QuestionSendingSerializer, LogoutSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from django.http import HttpResponse
from smtplib import SMTPException

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password





# Check if a role has a specific permission on a page.
def is_permission(role_name, page_title, permission_type):
    try:
        role = Role.objects.get(name=role_name)
    except:
        print( role_name,'not found in is_permission function')

    try:
        page = Page.objects.get(title=page_title)
    except:
        print( page_title,'page not found in is_permission function')

    try:
        role_page = RolePage.objects.get(role_id=role.id, page_id=page.id)
        if permission_type == 'can_create':
            return role_page.can_create
        elif permission_type == 'can_read':
            return role_page.can_read
        elif permission_type == 'can_update':
            return role_page.can_update
        elif permission_type == 'can_delete':
            return role_page.can_delete
    except:
        print('role_page not found in is_permission function')


# ------------------- Send Email View ------------------------- #

def send_email(subject, message, email_from, recipient_list): 
    try:
        send_mail(subject, message, email_from, recipient_list)
        return True, 'Email sent successfully'
    except SMTPException as e:
        return False, f'Error: {str(e)}'
    


# -----------------  Get CSRF ApiView   ----------------- #
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

# def get_csrf_token(request):
#     csrf_token = get_token(request)
#     return JsonResponse({'csrfToken': csrf_token})

# -----------------  Logout ApiVidew   ----------------- #

class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)  # Add parentheses here

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Logout Successful"}, status=status.HTTP_204_NO_CONTENT)


# -----------------  Register ApiView   ----------------- #
class RegisterView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]

    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):

        # Get username and password from request data
        userName = request.data.get('username')
        password = request.data.get('password')

        if not userName or not password:
            return Response({"error: Both Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if AuthUser.objects.filter(username=userName).exists():
            return Response({"error: Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({"error: Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'can_create'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {'auth_user':user.id}
        if user:
            serializer1 = AdminSerializer(data = data)
            if serializer1.is_valid():
                serializer1.save()

                response_data = {
                    'message': 'Registration successful. You can now log in.',
                }

                return Response(response_data)



# -----------------  Signin ApiView   ----------------- #

class SigninView(APIView):
    def post(self, request, *args, **kwargs):

        # Get username and password from request data
        userName = request.data.get('username')
        password = request.data.get('password')

        # Check if both username and password are provided
        if not userName or not password:
            return Response({"error: Both Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = authenticate(username=userName, password=password)

        # If authentication is successful
        if user:
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # return Response({"message: Authentication Successful"},status=status.HTTP_200_OK)

            # Return tokens and user data
            admin_user_serializer = UserSerializer(user)

            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': admin_user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error: Invalid Credintials"},status=status.HTTP_401_UNAUTHORIZED)



# -----------------  Page Model ApiView   ----------------- #

class PageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # Check if the user has permission to access the page
        # if not is_permission(request.user.role, 'Pages', 'can_read'):
        #     return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        selected_pages = Page.objects.filter(rolepage__role_id=request.user.role.id, rolepage__can_read=True)
        serializer = PageSerializer(selected_pages, many=True)
        return Response(serializer.data)


class PageRetrieveUpdateDeleteView(APIView):

    # permission_classes = [IsAuthenticated]

    # def get_object(self, pk):
    #     try:
    #         return Page.objects.get(pk=pk)
    #     except Page.DoesNotExist:
    #         return None

    # def get(self, request, pk, format=None):
    #     page = self.get_object(pk)
    #     if page:
    #         serializer = PageSerializer(page)
    #         return Response(serializer.data)
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # def put(self, request, pk, format=None):
    #     page = self.get_object(pk)
    #     if page:
    #         serializer = PageSerializer(page, data=request.data)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        page = self.get_object(pk)
        if page:
            page.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class QuestionListCreateView(APIView):

    def get(self, request, format=None):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


# ------------------- Question Creating view ------------------------- #

class QuestionCreatingView(APIView):

    def post(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_create'):
            return Response({"error":"You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        question = request.data.get('question')
        answers = request.data.get('answers')

        #Adding selected_order = 0 to the question data
        question['selected_order'] = 0

        question_serializer = QuestionSerializer(data = question)

        if(question_serializer.is_valid()):

            #Saving the question to the database
            question_instance = question_serializer.save()

            #Adding question id to every answer
            for answer in answers:
                    answer['question'] = question_instance.id

            answer_serializer = AnswerSerializer(data = answers, many = True)

            if(answer_serializer.is_valid()):

                #Saving the answers in the database
                answer_serializer.save()

                return Response({'success': 'Question created successfully'}, status=201)
            else:
                question_instance.delete()
                return Response({'error':'Answers are not valid'}, answer_serializer.errors,status=400)

        else:
            print(question_serializer.errors)
            return Response( {'error':'Question is not valid'},question_serializer.errors, status = 400)



# ------------------- Question Sending view ------------------------- #

class QuestionSendingView(APIView):

    def get(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_read'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        #Get the question ids that are already in the quiz qanda table
        q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

        # Getting the questions that can be updated (excluding the questions that are already taken by users)
        questions = Question.objects.exclude(id__in = q_and_a_question_id_list)

        question_sending_serializer = QuestionSendingSerializer(questions, many=True)

        return Response(question_sending_serializer.data, status=200)



# ------------------- Question Updating view ------------------------- #

class QuestionUpdatingView(APIView):

    def post(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_update'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        #Get the data into variables
        question_id = request.data.get('question_id')
        question = request.data.get('question')
        answers = request.data.get('answers', {})

        try:

            #Getting the question object related to that id
            question_object = Question.objects.get(id = question_id)

            #Making is_updating true on every question field
            make_is_updating_true()

            #Get the question ids that are in the quiz q and a table
            q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

            #Check if the question id is not in the quiz q and a table
            if question_object.id not in q_and_a_question_id_list:

                #Put the data into serializers and check the validation
                question_update_serializer = QuestionSerializer(question_object, data=question, partial=True)

                if(question_update_serializer.is_valid()):

                    #Adding question id to every answer
                    for answer in answers:
                        answer['question'] = question_id

                    answer_replacing_serializer = AnswerSerializer(data=answers, many=True)

                    if(answer_replacing_serializer.is_valid()):

                        #Delete the entire set of answers for this question
                        Answer.objects.filter(question=question_object.id).delete()

                        #Saving the two serializers
                        question_update_serializer.save()
                        answer_replacing_serializer.save()

                        #add the last updated timestamp to every question and also make is_updating false
                        make_is_updating_false_and_timestamp()

                        return Response({'status': 'success'}, status=201)

                    else:
                        make_is_updating_false_and_timestamp()
                        return Response(answer_replacing_serializer.errors, status=400)
                else:
                    make_is_updating_false_and_timestamp()
                    return Response(question_update_serializer.errors, status=400)
            else:
                make_is_updating_false_and_timestamp()
                return Response({'error':'Question has been taken by a user very recently'}, status=400)

        except Question.DoesNotExist:
            return Response({'error':'no question found'}, status=400)



# ------------------- Question Deleting view ------------------------- #

class QuestionDeleteView(APIView):

    def post(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_delete'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        #Getting the question id into a variable

        question_id = request.data.get('question_id')
        print(question_id)

        try:
            #Get the object of that question id
            question_object = Question.objects.get(id=question_id)

            #make is_updating True
            make_is_updating_true()

            #Get the question ids that are in the quiz q and a table
            q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

            #Check if the question is in the quiz q and a table
            if question_object.id not in q_and_a_question_id_list:

                #Delete all the answers related to this question
                Answer.objects.filter(question=question_object.id).delete()

                #Delete the question from the question table
                question_object.delete()

                make_is_updating_false_and_timestamp()

                return Response({'status': 'success'}, status=201)

            else:
                make_is_updating_false_and_timestamp()
                return Response({'Question has been taken by a user very recently'}, status=400)

        except Question.DoesNotExist:
                return Response({'No question found'}, status=400)



# ------------------- Question selecting view ------------------------- #

class QuestionSelectingView(APIView):

    def get(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_read'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        #getting the selected questions
        selected_question_objects = Question.objects.exclude(selected_order = 0).order_by('selected_order')

        selected_question_list = []

        #the selected question ids
        for selected_question in selected_question_objects:
            selected_question_list.append({'id' : str(selected_question.id)})

        #getting all of the questions
        question_objects = Question.objects.all()

        all_question_sending_serializer = QuestionSendingSerializer(question_objects, many=True)

        return Response({'selected_questions':selected_question_list, 'all_questions': all_question_sending_serializer.data}, status=200)


    def post(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz', 'can_update'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)


        #Getting the list of question ids to a variable
        selected_question_id_list = request.data.get('selected_question_id_list')

        make_is_updating_true()

        #Update all the question's selected_order attribute to 0
        for question in Question.objects.all():

            question.selected_order = 0
            question.save()

        #Updating the selected order of the relavant questions
        for i in range(len(selected_question_id_list)):

            try:
                selected_question_object = Question.objects.get(id = selected_question_id_list[i]['id'])
                selected_question_object.selected_order = i+1
                selected_question_object.save()

            except Question.DoesNotExist:
                make_is_updating_false_and_timestamp()
                return Response({'error':'Question Not Found'}, status=400)

        make_is_updating_false_and_timestamp()
        return Response({'status':'success'}, status=201)


#Function that sets is_updating true in all the question fields
def make_is_updating_true():
    for question in Question.objects.all():
        question.is_updating = True
        question.save()


#Function that sets is_updating false and sets the timestamp
def make_is_updating_false_and_timestamp():
    last_updated_timestamp = timezone.now()

    for question in Question.objects.all():
        question.is_updating = False
        question.last_updated_timestamp = last_updated_timestamp
        question.save()



# -----------------  Role Model ApiView   ----------------- #

class RoleListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Roles', 'can_read'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)
  
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Roles', 'can_create'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)


        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():

            role = serializer.save()

            # Get the page data from the request
            pages_data = request.data.get('pages', [])
            # Extract the page ids from the pages data
            page_ids = [page.get('id') for page in pages_data]

            if page_ids:
                # Retrieve pages based on the provided ids
                pages = Page.objects.filter(id__in=page_ids)

                # Loop through the pages and create/update RolePage entries
                for page in pages:
                    page_data = next(item for item in pages_data if item['id'] == page.id)
                    # Get or create RolePage instance
                    role_page, created = RolePage.objects.get_or_create(role=role, page=page)
                    # Set permissions based on the provided data
                    role_page.create = page_data.get('create', False)
                    role_page.read = page_data.get('read', False)
                    role_page.update = page_data.get('update', False)
                    role_page.delete = page_data.get('delete', False)
                    # Save the RolePage instance
                    role_page.save()

            # Return a response with the serialized role data
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # If the data is not valid, return a response with the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleRetrieveUpdateDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        role = self.get_object(pk)
        if role:
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        role = self.get_object(pk)
        print('data', request.data)
        if role:
            serializer = RoleSerializer(role, data=request.data)
            if serializer.is_valid():

                role = serializer.save()

                # Get the page data from the request
                pages_data = request.data.get('pages', [])
                # Extract the page ids from the pages data
                page_ids = [page.get('id') for page in pages_data]

                if page_ids:
                    # Retrieve pages based on the provided ids
                    pages = Page.objects.filter(id__in=page_ids)

                    # Loop through the pages and create/update RolePage entries
                    for page in pages:
                        page_data = next(item for item in pages_data if item['id'] == page.id)
                        # Get or create RolePage instance
                        role_page, created = RolePage.objects.get_or_create(role=role, page=page)
                        # Set permissions based on the provided data
                        role_page.create = page_data.get('create', False)
                        role_page.read = page_data.get('read', False)
                        role_page.update = page_data.get('update', False)
                        role_page.delete = page_data.get('delete', False)
                        # Save the RolePage instance
                        role_page.save()

                return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Roles', 'can_delete'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        print('pk', pk)
        role = self.get_object(pk)
        if role:
            role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)



# -----------------  Results Model ApiView   ----------------- #
class ResultsListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz Result', 'can_read'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        results = QuizResult.objects.all().order_by('-date', '-time')
        serializer = QuizResultSerializer(results, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = QuizResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResultsRetrieveUpdateDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return QuizResult.objects.get(pk=pk)
        except QuizResult.DoesNotExist:
            return None

    def get(self, request, pk, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Quiz Result', 'can_read'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        result = self.get_object(pk)
        if result:
            serializer = QuizResultSerializer(result)
            questions_and_answers = []
            q_and_a_objects = QuizQandA.objects.filter(quiz_result = result.id)
            for q_and_a in q_and_a_objects:
                answer = Answer.objects.get(id = q_and_a.answer_id)
                questions_and_answers.append({
                    'question': q_and_a.question.question,
                    'answer': answer.answer,
                })
            print('questions_and_answers',questions_and_answers)
            return Response({'quiz_result_data': serializer.data, 'questions_and_answers': questions_and_answers})
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        result = self.get_object(pk)
        if result:
            serializer = QuizResultSerializer(result, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)


class SetAppointment(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            print(f"Appointment with pk={pk} does not exist.")
            raise Http404


    def put(self, request, pk, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Appointments', 'can_update'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        appointment = Appointment.objects.get(id = pk)
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)  # Add this line to print validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            print(f"Appointment with pk={pk} does not exist.")
            raise Http404

    def get(self, request, format=None):
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        # print(serializer.data)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors)  # Add this line to print validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AccountsView(generics.UpdateAPIView):

    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'can_read'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        accounts = AuthUser.objects.all()
        serializer = UserSerializer(accounts, many=True)
        return Response(serializer.data)

class AccountRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, pk,):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'can_read'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        user_details = AuthUser.objects.get(id=pk)
        serializer = UserSerializer(user_details)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):

        user_details = AuthUser.objects.get(id=pk)
        if user_details.id == 1 :
            return Response({"error": "You cannot update the default admin user"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'can_update'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_details = AuthUser.objects.get(id=pk)
        except AuthUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract 'role' from request.data
        role_id = request.data.get('role')

        try:
            # Try to get the Role instance by ID
            role_instance = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Update 'role' field with the Role instance
        user_details.role = role_instance
        user_details.save()

        serializer = UserSerializer(user_details)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):

        user_details = AuthUser.objects.get(id=pk)
        if user_details.id == 1 :
            return Response({"error": "You cannot delete the default admin user"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'can_delete'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_details = AuthUser.objects.get(id=pk)
        except AuthUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        admin = Admin.objects.get(auth_user = pk)
        if admin.profile_image:
            admin.profile_image.delete()
        user_details.delete()

        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pending_appointments(request):

    # Check if the user has permission to access the page
    if not is_permission(request.user.role, 'Appointments', 'can_read'):
        return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        appointments = Appointment.objects.filter(admin__auth_user = request.user.id, is_checked = False)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_completed_appointments(request):

    # Check if the user has permission to access the page
    if not is_permission(request.user.role, 'Appointments', 'can_read'):
        return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        appointments = Appointment.objects.filter(admin__auth_user = request.user.id, is_checked = True)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_appointment_details(request, pk):
    if request.method == 'GET':
        appointment = Appointment.objects.get(id = pk)

        questions_and_answers = []
        quiz_result_id = appointment.quiz_result
        q_and_a_objects = QuizQandA.objects.filter(quiz_result = quiz_result_id)
        for q_and_a in q_and_a_objects:
            answer = Answer.objects.get(id = q_and_a.answer_id)
            questions_and_answers.append({
                'question': q_and_a.question.question,
                'answer': answer.answer,
            })
        serializer = UserAppointments(appointment)
        # print(serializer.data)
        print(questions_and_answers)
        return Response({'appointment_data': serializer.data, 'questions_and_answers': questions_and_answers})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    if request.method == 'GET':
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_current_user(request):
    if request.method == 'PUT':
        user = request.user
        admin = Admin.objects.get(auth_user=user)
        print(request.data)

        # Check if 'profile_image' is present and not equal to 'null'
        if 'profile_image' in request.data or request.data['profile_image'] != 'null':
            # Delete the existing profile image
            if admin.profile_image:
                admin.profile_image.delete()

        # Use a single serializer, excluding 'profile_image' if needed
        serializer = UpdateCurrentUserSerializer(admin, data=request.data, partial=True, exclude_profile_image=request.data['profile_image'] == 'null')

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_role_pages(request, pk):
    if request.method == 'GET':
        permission_pages = RolePage.objects.filter(role_id = pk)
        serializer = RolePageSerializer(permission_pages, many=True)
        return Response(serializer.data)


class PrivateQuestionListCreateView(APIView):
    def get(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Private Questions', 'can_read'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        questions = PrivateQuestions.objects.filter(admin__auth_user = request.user).order_by('-asked_date')
        serializer = PrivateQuestionsSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Private Questions', 'can_create'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrivateQuestionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivateQuestionsRetrieveUpdateDestroyView(APIView):
    def get_object(self, pk):
        try:
            return PrivateQuestions.objects.get(pk=pk)
        except PrivateQuestions.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Private Questions', 'can_update'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        try:
            question = PrivateQuestions.objects.get(pk=pk)
        except PrivateQuestions.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PrivateQuestionsUpdateSerializer(question, data=request.data)
        if serializer.is_valid():
            # Save the serializer data
            serializer.save()

            # Set is_patient_viewed to False
            question.is_patient_viewed = False
            question.save()

            return Response({"success": "Question updated successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_appointments_count (request):
    if request.method == 'GET':
        # count all appointments for the user
        user = request.user
        appointments = Appointment.objects.filter(admin__auth_user = user, is_checked = False)
        return Response({'count': appointments.count()})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_private_questions_count (request):
    if request.method == 'GET':
        # count all private questions for the user
        user = request.user
        questions = PrivateQuestions.objects.filter(admin__auth_user = user, is_checked = False)
        return Response({'count': questions.count()})
    

# ------------------- Reset Password View ------------------------- #

@ensure_csrf_cookie
@csrf_exempt
def send_otp(request):

    if request.method == 'POST':
         # Get the JSON data from the request body
        data = json.loads(request.body)
        # Extract the 'email' field from the JSON data
        email = data.get('email', '')
        try:
            user = AuthUser.objects.get(email=email)

            if user:
                otp = randint(100000, 999999)
                user.otp = otp
                user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=5)
                user.save()

                subject = 'Mind Care OTP'
                message = f'Your OTP is {otp}'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email]
                send_email(subject, message, email_from, recipient_list)

                success, message = send_email(subject, message, email_from, recipient_list)
                if success:
                    return HttpResponse({'message :  The otp has been sent to your email'}, status=200)
                else:
                    print(message)
                    return HttpResponse({'Email sent not successful'}, status=500)
            else:
                return HttpResponse({'User does not exist'}, status=404)
        except AuthUser.DoesNotExist:
            return HttpResponse({'User does not exist'}, status=404)
        

def verify_otp(email, otp):
    try:
        user = AuthUser.objects.get(email=email)
        if user.otp == int(otp):
            if timezone.now() <= user.otp_expires_at:
                return True, 'OTP verified successfully'
            else:
                # print('OTP expired')
                return False , 'OTP expired'
        else:
            # print('OTP does not match')
            return False, 'OTP does not match'
            
    except AuthUser.DoesNotExist:
        # print('User does not exist')
        return False, 'User does not exist'


@ensure_csrf_cookie
@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        new_password = data.get('password')
        otp = data.get('otp')

        if not email or not new_password or not otp: 
            return HttpResponse({'Please enter all fields'}, status=400)

        # Validate password format
        try:
            validate_password(new_password)
        except ValidationError:
            return JsonResponse({'Password format not valid'}, status=400)

        try:
            success, message = verify_otp(email, otp)
            if not success:
                return HttpResponse({message}, status=400)
            
            user = AuthUser.objects.get(email=email)

            if user:
                user.set_password(new_password)
                user.save()
                return HttpResponse({'Password reset successful'}, status=200)
            else:
                return HttpResponse({'User does not exist'}, status=404)
            
        except AuthUser.DoesNotExist:
            return HttpResponse({'User does not exist'}, status=404)
    

