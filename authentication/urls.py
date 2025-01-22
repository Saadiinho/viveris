from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpAPIView, SignInAPIView, UserDetailView,get_user_points



urlpatterns = [
    path('users/sign-up/', SignUpAPIView.as_view(), name='inscription'),
    path('users/sign-in/', SignInAPIView.as_view(), name='connexion'),
    path('users/profile/', UserDetailView.as_view(), name='information_profile'),
    path('users/points/', get_user_points, name='get_user_points'),
    
]