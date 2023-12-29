from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import AuthUser, Page, Role, RolePage
from .web_app_serializers import PageSerializer, RoleSerializer, UserSerializer
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
    

