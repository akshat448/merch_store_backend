from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('register' , views.register , name='register'),
    path('login' , views.login , name='login'),
    path('logout' , views.logout , name='logout'),
    path("change_password",views.change_pass , name='change_password')
]