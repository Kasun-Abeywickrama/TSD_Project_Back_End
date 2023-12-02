import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from tsd_project import settings
from .models import CustomUser

#Creating the jwt token authentication
#Jwt token will be authenticated within each request made by the user
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
            
            #Getting the user_id from the payload
            user_id = payload.get('user_id')

            #Checking whether a user exists with that user_id and creating the user object which consists of all the table records
            user = CustomUser.objects.get(pk = user_id)

            #If there is a user with that id return the user object, otherwise return none
            return user, None
        
        #Handle the exceptions respectively
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has Expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('No such user')