from django.urls import path
from django.contrib import admin
from .views import LoginTokenView, LogoutView, UserDetails

urlpatterns = [
    path('login-token/', LoginTokenView.as_view(), name='login-token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetails.as_view(), name='user-details'),
]
