# places where template files or urls are required I have marked with ##

from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from .models import CustomUser as User

def login(request):
    '''login'''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        #user authentication using email
        user = auth.authenticate(email = email , password = password)
        if user!= None:
            auth.login(request, user)
            return redirect('/')            ## redirect to home
        else:
            messages.warning(request , 'Invalid Credentials')
            return redirect('/login')       ## refreshs page and display message
    else:
        return render(request , 'login.html')  ## first time login session
    

def logout(request):
    '''logout'''
    auth.logout(request)
    return redirect('/')        ##


def change_pass(request):
    '''change password if currently logged in'''
    if request.method == "POST":
        
        #checking and getting logged in user
        user = request.user
        if user is None:
            messages.warning(request , "Please login to change password.")
            return redirect("/login")                              ## 

        old_password = request.POST['old_pass']
        new_password = request.POST['new_pass']
        confirm_password = request.POST['confirm_pass']
        
        #validating password before changing
        if auth.authenticate(email= user.email , password = old_password) ==None:
            messages.warning(request,"Enter correct old password.")
            return redirect("/change_password")                  ##
        elif new_password != confirm_password:
            messages.warning(request , "Please match the passwords and try again")
            return redirect("/change_password")                  ##
        else:
            user.set_password(new_password)
            user.save()
            messages.info(request , "Password reset successfully")
            return redirect("/login")                                   ## 
    else:
        return render(request , 'change_password.html')     ##


def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['emailid']
        mobile_num = request.POST['mobile_num']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.warning(request , "Please match the passwords and try again")
            return redirect('/register')                                ##
        elif User.objects.filter(email=email).exists():
            messages.info(request , "Email is already registered.")
            return redirect('/register')                                ##
        elif User.objects.filter(Phone_Num=mobile_num).exists():
            messages.info(request , "This mobile number is already registered.")
            return redirect('/register')                                ##
        else:
            User.objects.create_user(password=password , email=email, Phone_Num = mobile_num , name = name)
            messages.info(request , "User registered successfully!!")
            return redirect('/login')                                   ##
    else:
        return render(request, 'register.html')                         ##