from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser as User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password

from .serializers import UserSerializer

class RegisterView(APIView):

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        mobile_num = request.data.get('mobile_num')
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

        return Response(data, status=status.HTTP_200_OK)


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')
        user = request.user
        if not check_password(old_password, user.password):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != new_password2:
            return Response({"new_password": ["New passwords must match."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(status=status.HTTP_200_OK)


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)