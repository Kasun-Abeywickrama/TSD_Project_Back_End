from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from .models import Page
from .web_app_serializers import AdminUserSerializer, PageSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



class AdminUserSigninView(APIView):
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
            admin_user_serializer = AdminUserSerializer(user)

            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': admin_user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error: Invalid Credintials"},status=status.HTTP_401_UNAUTHORIZED)



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