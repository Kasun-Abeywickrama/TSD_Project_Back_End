from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import AuthUser, Page, Role
from .web_app_serializers import PageSerializer, RoleSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions

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

# -----------------  Signup ApiView   ----------------- #

class RegisterView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]

    queryset = AuthUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
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
        pages = Page.objects.all()
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        serializer = PageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PageRetrieveUpdateDeleteView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Page.objects.get(pk=pk)
        except Page.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        page = self.get_object(pk)
        if page:
            serializer = PageSerializer(page)
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        page = self.get_object(pk)
        if page:
            serializer = PageSerializer(page, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

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
        pages = Role.objects.all()
        serializer = RoleSerializer(pages, many=True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    


