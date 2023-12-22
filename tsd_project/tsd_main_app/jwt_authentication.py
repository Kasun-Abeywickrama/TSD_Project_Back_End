import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from tsd_project import settings
from .models import AuthUser, User

#Creating the jwt token authentication
#Jwt token will be authenticated within each request made by the user, counselor, admin
class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):

        #getting the jwt token from the request header
        token = request.headers.get('Authorization')

        #If the token start with bearer, cut out the bearer string part of the token
        if token and token.startswith('Bearer '):
            token = token.split('Bearer ')[1]

        if not token:
            return None
        
        try:
            #Decoding the jwt token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms = ['HS256'])

            #Getting the auth user id from the payload
            auth_user_id = payload.get('auth_user_id')

            #Checking whether a auth user exists with that auth_user_id and creating the auth user object which consists of all the table records
            authuser = AuthUser.objects.get(pk = auth_user_id)

            #If there is a auth user with that id return the auth user object, raise exception
            if authuser:
                return authuser, None
            else:
                raise AuthenticationFailed('Auth user does not Exists')
            
        #Handle the exceptions respectively
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has Expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')