from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout

from .serializers import UserSerializer
from .backend import SSOAuthenticationBackend
from .models import CustomUser as User

from dotenv import load_dotenv
import os, requests
load_dotenv()


class LoginTokenView(APIView):
    def post(self, request):
        sso_token = request.data.get('token')
        if not sso_token:
            return Response({'error': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, sso_token=sso_token)
        if user is None:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        print(f"User {user} logged in successfully with ID: {user.pk}")

        token, _ = Token.objects.get_or_create(user=user)

        serializer = UserSerializer(user)
        user.save()
        
        return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        token =Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
"""class LoginTokenView(APIView):
    def post(self, request):
        # Extracting token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Token '):
            sso_token = auth_header.split(' ')[1]
        else:
            return Response({'error': 'Token not found or incorrect format'}, status=status.HTTP_400_BAD_REQUEST)
        
        backend = SSOAuthenticationBackend()
        user = backend.authenticate(request, sso_token=sso_token)
        
        if user is None:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)

        data = {
            'key': token.key,
            'name': user.name,
            'email': user.email
        }

        return Response(data, status=status.HTTP_200_OK)"""    
    
"""class RegisterView(APIView):

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        mobile_num = request.data.get('phone_no')
        position = request.data.get('position')
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if not all([name, email, mobile_num, position, password, password2]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'This Email ID is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone_no=mobile_num).exists():
            return Response({'error': 'This Mobile Number is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(
            password=password, 
            email=email, 
            phone_no=mobile_num, 
            name=name, 
            position=position
        )
        # Create a token for the new user
        token, created = Token.objects.get_or_create(user=user)
        data = {
            'key': token.key,
            'name': user.name,
            'email': user.email
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = Token.objects.get_or_create(user=user)

        data = {
            'key': token[0].key,
            'name': user.name,
            'email': user.email
        }

        return Response(data, status=status.HTTP_200_OK)"""
