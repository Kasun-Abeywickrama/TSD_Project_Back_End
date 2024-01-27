from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Admin, Appointment, AuthUser, Page, QuizResult, Role, RolePage, Question, Answer, QuizQandA
from .web_app_serializers import AdminSerializer, AppointmentSerializer, PageSerializer, QuizResultSerializer, RoleSerializer, UpdateCurrentUserSerializer, UserAppointments, UserSerializer, QuestionSerializer, AnswerSerializer, QuestionSendingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


# Check if a role has a specific permission on a page.
def is_permission(role_name, page_title, permission_type):
    try:
        role = Role.objects.get(name=role_name)
    except:
        print('role not found in is_permission function')

    try:
        page = Page.objects.get(title=page_title)
    except:
        print('page not found in is_permission function')

    try:
        role_page = RolePage.objects.get(role_id=role.id, page_id=page.id)
        if permission_type == 'create':
            return role_page.create
        elif permission_type == 'read':
            return role_page.read
        elif permission_type == 'update':
            return role_page.update
        elif permission_type == 'delete':
            return role_page.delete
    except:
        print('role_page not found in is_permission function')



# -----------------  Logout ApiVidew   ----------------- #

class LogoutView(APIView):
     permission_classes = (IsAuthenticated,)
     def post(self, request):
          
          try:
               refresh_token = request.data["refresh_token"]
               token = RefreshToken(refresh_token)
               token.blacklist()
               return Response(status=status.HTTP_205_RESET_CONTENT)
          except Exception as e:
               return Response(status=status.HTTP_400_BAD_REQUEST)



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

        # if not userName or not password:
        #     return Response({"error: Both Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # if AuthUser.objects.filter(username=userName).exists():
        #     return Response({"error: Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # if len(password) < 8:
        #     return Response({"error: Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

        # # Check if the user has permission to access the page
        # if not is_permission(request.user.role, 'Accounts', 'create'):
        #     return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

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

        selected_pages = Page.objects.filter(rolepage__role_id=request.user.role.id, rolepage__read=True)
        serializer = PageSerializer(selected_pages, many=True)
        return Response(serializer.data)
    
    # def post(self,request,format=None):
    #     serializer = PageSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(answer_serializer.errors,status=400)
                    
        else:
            print(question_serializer.errors)
            return Response(question_serializer.errors, status = 400)
        

        
# ------------------- Question Sending view ------------------------- #

class QuestionSendingView(APIView):

    def get(self, request):

        #Get the question ids that are already in the quiz qanda table
        q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

        # Getting the questions that can be updated (excluding the questions that are already taken by users)
        questions = Question.objects.exclude(id__in = q_and_a_question_id_list)

        question_sending_serializer = QuestionSendingSerializer(questions, many=True)

        return Response(question_sending_serializer.data, status=200)
    


# ------------------- Question Updating view ------------------------- #

class QuestionUpdatingView(APIView):

    def post(self, request):

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
                return Response({'Question has been taken by a user very recently'}, status=400)
            
        except Question.DoesNotExist:
            return Response({'no question found'}, status=400)
        


# ------------------- Question Deleting view ------------------------- #
        
class QuestionDeleteView(APIView):

    def post(self, request):

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
                return Response({'Question Not Found'}, status=400)

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
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Roles', 'create'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        
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
        if role:
            serializer = RoleSerializer(role, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        role = self.get_object(pk)
        if role:
            role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    


# -----------------  Results Model ApiView   ----------------- #
class ResultsListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        results = QuizResult.objects.all()
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
        result = self.get_object(pk)
        if result:
            serializer = QuizResultSerializer(result)
            return Response(serializer.data)
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
        appointment = self.get_object(pk)
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
        if not is_permission(request.user.role, 'Accounts', 'read'):
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
        if not is_permission(request.user.role, 'Accounts', 'read'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)
        user_details = AuthUser.objects.get(id=pk)
        serializer = UserSerializer(user_details)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'update'):
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
        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'delete'):
            return Response({"error": "You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        try:
            user_details = AuthUser.objects.get(id=pk)
        except AuthUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        user_details.delete()

        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_pending_appointments(request):
    if request.method == 'GET':
        appointments = Appointment.objects.filter(admin__auth_user = request.user.id, is_checked = False)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_completed_appointments(request):
    if request.method == 'GET':
        appointments = Appointment.objects.filter(admin__auth_user = request.user.id, is_checked = True)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_appointment_details(request, pk):
    if request.method == 'GET':
        appointment = Appointment.objects.get(id = pk)
        serializer = UserAppointments(appointment)
        return Response(serializer.data)


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
        if 'profile_image' in request.data and request.data['profile_image'] != 'null':
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