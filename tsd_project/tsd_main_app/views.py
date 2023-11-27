
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
import jwt
from django.http import JsonResponse
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from tsd_main_app.serializers import LoginSerializer, CustomUserSerializer


# Creating the view to register the user
@api_view(['POST'])
def register_user(request):
        
        # Putting the data set inside the serializer
        custom_user_serializer = CustomUserSerializer(data = request.data)

        # Checking if the data are valid (this will automatically check whether the username is available)
        if(custom_user_serializer.is_valid()):

            # Creating the new records in the tables
            custom_user_serializer.save()

            # Returning a success response to the fluttter terminal
            return JsonResponse({'status': 'success'}, status=201)
        else:
            # If the data is not valid, sending the relavant error to the frontend
            return JsonResponse({'status': 'Data is not valid','errors': custom_user_serializer.errors}, status=400)
    


# Creating the view to login the user
@api_view(['POST'])
def login_user(request):

    # Putting the login information to the serailizer
    login_serializer = LoginSerializer(data = request.data)

    #Checking if the data is valid
    if(login_serializer.is_valid()):
        username = login_serializer.validated_data['username']
        password = login_serializer.validated_data['password']

        # Authenticating the user
        customuser = authenticate(request, username=username, password=password)
    
        # Displaying results in the  Django terminal
        print(f'username: {username}, Password: {password}')
        print(f'Authentication Result: {customuser}')
    
        # If there is a user,
        if customuser is not None:
            # create a JWT token
            token = generate_jwt_token(customuser)

            # create and send a login response including the token
            login(request, customuser)
            return JsonResponse({'status': 'success', 'token': token}, status=200)
    
        # If there is not, 
        else:
            # create and send an error response
            return JsonResponse({'error': 'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
    # If the data is not valid
    else:
         return JsonResponse({'status': 'Data is not valid'}, status=400)
        



# Function that creates a JWT token
def generate_jwt_token(customuser):
    # Including the username in the payload
    payload = {
        'username' : customuser.username
    }

    # generate the JWT token
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm = 'HS256')

    # Returning the token
    return token
