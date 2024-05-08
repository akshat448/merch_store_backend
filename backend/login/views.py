from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser as User
from django.contrib.auth import authenticate

from .serializers import UserSerializer

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
        user = authenticate(request, email=user.email, password=old_password)
        if user is None:
            return Response({'error': 'Incorrect old password'}, status=status.HTTP_400_BAD_REQUEST)
        elif new_password != new_password2:
            return Response({'error': 'Please match new passwords!!'}, status=status.HTTP_400_BAD_REQUEST)
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
    
class RegisterView(APIView):

    def post(self,request):
        name = request.POST['name']
        email = request.POST['emailid']
        mobile_num = request.POST['mobile_num']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            return Response({'error': 'Please match your passwords and try again'}, status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(email=email).exists():
            return Response({'error': 'This Email ID is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        elif User.objects.filter(Phone_Num=mobile_num).exists():
            return Response({'error': 'This Mobile Number is already registered'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            User.objects.create_user(password=password , email=email, Phone_Num = mobile_num , name = name)
            return Response(status=status.HTTP_200_OK)