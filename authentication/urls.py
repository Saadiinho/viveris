from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView, SignUpAPIView, SignInAPIView, UpdateUserProfileView, UserDetailView,get_user_points



urlpatterns = [
    # Existing URLs...
    path('users/sign-up/', SignUpAPIView.as_view(), name='inscription'),
    path('users/sign-in/', SignInAPIView.as_view(), name='connexion'),
    path('users/profile/', UserDetailView.as_view(), name='information_profile'),
    path('users/points/', get_user_points, name='get_user_points'),
    
    # New URLs for updating profile and password
    path('users/profile/update/', UpdateUserProfileView.as_view(), name='update_profile'),
    path('users/profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
]