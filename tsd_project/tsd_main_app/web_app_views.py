from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import AuthUser, Page, Role, RolePage, Question, Answer, QuizQandA
from .web_app_serializers import PageSerializer, RoleSerializer, UserSerializer, QuestionSerializer, AnswerSerializer, QuestionSendingSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions

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

        if not userName or not password:
            return Response({"error: Both Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if AuthUser.objects.filter(username=userName).exists():
            return Response({"error: Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            return Response({"error: Password must be at least 8 characters"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has permission to access the page
        if not is_permission(request.user.role, 'Accounts', 'create'):
            return Response({"error: You do not have permission to access this page"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
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
    




# ------------------- Question Creating view ------------------------- #
    
class QuestionCreatingView(APIView):

    def post(self, request):

        question = request.data.get('question')
        answers = request.data.get('answers', {})

        question_serializer = QuestionSerializer(data = question)

        if(question_serializer.is_valid()):

            question_instance = question_serializer.save()

            for answer in answers:
                    answer['question'] = question_instance.id

            answer_serializer = AnswerSerializer(data = answers, many = True)

            if(answer_serializer.is_valid()):

                answer_serializer.save()

                return Response({'success': 'Question created successfully'}, status=201)
            else:
                question_instance.delete()
                return Response(answer_serializer.errors,status=400)
                    
        else:
            return Response(question_serializer.errors, status = 400)
        

        

# ------------------- Question Sending view ------------------------- #

class QuestionSendingView(APIView):

    def get(self, request):

        #Get the question ids that are already in the quiz qanda table
        q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

        # Getting the questions that can be updated (excluding the questions that are already taken by users)
        questions = Question.objects.exclude(id__in = q_and_a_question_id_list)

        question_sending_serializer = QuestionSendingSerializer(data=questions, many=True)

        return Response(question_sending_serializer.data, status=200)
    


# ------------------- Question Updating view ------------------------- #

class QuestionUpdatingView(APIView):

    def post(self, request):

        #Get the data into variables
        question_id = request.data.get('question_id')
        question = request.data.get('question'),
        answers = request.data.get('answers', {})

        #Getting the question object related to that id
        question_object = Question.objects.get(id = question_id)

        #Check if there is a question object like that
        if question_object is not None:

            #Get the question ids that are in the quiz q and a table
            q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

            #Check if the question id is not in the quiz q and a table
            if question_object.id not in q_and_a_question_id_list:
                
                #Put the data into serializers and check the validation
                question_update_serializer = QuestionSerializer(question_object, data=question, partial=True)

                if(question_update_serializer.is_valid()):

                    answer_replacing_serializer = AnswerSerializer(data=answers, many=True)

                    if(answer_replacing_serializer.is_valid()):

                        #Delete the entire set of answers for this question
                        Answer.objects.filter(question=question_object.id).delete()

                        #Saving the two serializers
                        question_update_serializer.save()
                        answer_replacing_serializer.save()

                        return Response({'status': 'success'}, status=201)

                    else:
                        return Response(answer_replacing_serializer.errors, status=400)
                else:
                    return Response(question_update_serializer.errors, status=400)
            else:
                return Response({'Error':'Question has been taken by a user very rcently'}, status=400)
        else:
            return Response({'Error':'no question object found'}, status=400)
        


# ------------------- Question Deleting view ------------------------- #
        
class QuestionDeleteView(APIView):

    def delete(self, request):

        #Getting the question id into a variable

        question_id = request.data.get('question_id')

        #Get the object of that question id
        question_object = Question.objects.get(id=question_id)

        #Check if the question exists
        if question_object is not None:

            #Get the question ids that are in the quiz q and a table
            q_and_a_question_id_list = QuizQandA.objects.values_list('question', flat=True)

            #Check if the question is in the quiz q and a table
            if question_object.id not in q_and_a_question_id_list:

                #Delete all the answers related to this question
                Answer.objects.filter(question=question_object.id).delete()

                #Delete the question from the question table
                question_object.delete()

                return Response({'status': 'success'}, status=201)
            
            else:
                return Response({'Error':'Question has been taken by a user very rcently'}, status=400)
        else:
            return Response({'Error':'no question object found'}, status=400)
        


# ------------------- Question selecting view ------------------------- #

class QuestionSelectingView(APIView):

    def get(self, request):

        #getting the selected questions
        question_objects = Question.objects.exclude(selected_order = 0).order_by('selected_order')

        #Sending the questions and answers through the serializers
        selected_question_sending_serializer = QuestionSendingSerializer(data=question_objects, many=True)

        return Response(selected_question_sending_serializer.data, status=200)
    

    def post(self, request):

        #Getting the list of question ids to a variable
        selected_question_id_list = request.data

        #Update all the question's selected_order attribute to 0
        for question in Question.objects.all():

            question.selected_order = 0
            question.save()

        #Updating the selected order of the relavant questions
        for i in range(len(selected_question_id_list)):

            selected_question_object = Question.objects.get(id = selected_question_id_list[i]['question_id'])
            if selected_question_object is not None:
                selected_question_object.selected_order = i+1
                selected_question_object.save()
            else:
                return Response({'Error': 'No object found for that question id'}, status=400)

        return Response({'status':'success'}, status=201)




                







        

    

    



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
    

