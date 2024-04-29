# from django.shortcuts import render, redirect
# from django.contrib.auth.models import auth
# from django.contrib import messages

# def login(request):
#     '''login'''
#     if request.method == 'POST':
#         email = request.POST['email']
#         pasword = request.POST['pasword']

#         #user authentication using email
#         user = auth.authenticate(email = email , password = pasword)
#         if user!= None:
#             auth.login(request, user)
#             return redirect('/')            # redirect to home
#         else:
#             messages.warning(request , 'Invalid Credentials')
#             return redirect('/login')       #refresh page and display message
#     else:
#         return render(request , 'login.html')  #first time login session
    
# def logout(request):
#     '''logout'''
#     auth.logout(request)
#     return redirect('/')

# def change_pass(request):
#     '''change password'''
#     if request.method == "POST":

#         user = request.user
#         old_password = request.old_pass
#         new_password = request.new_pass
#         confirm_password = request.confirm_pass

#         if new_password != confirm_password:
#             messages.warning(request , "Please match the passwords and try again")
        
        
#     else:
#         return render(request , 'change_password.html')

# def register(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['emailid']
#         mobile_num = request.POST['mobile_num']
#         password = request.POST['pasword']
#         password2 = request.POST['pasword2']
        
#         if password != password2:
#             messages.warning(request , "Please match the passwords and try again")
#             return redirect('/register')
#         elif User.objects.filter(email=email).exists():
#             messages.info(request , "Email already exists")
#             return redirect('/register')
#         elif User.objects.filter(username=username).exists():
#             messages.info(request , "This username already exists, please choose a different one")
#             return redirect('/register')
#         else:
#             User.objects.create_user(username=username , password=password , email=email, mobile_num = mobile_num)
#             return redirect('/login')
#     else:
#         return render(request, 'register.html')