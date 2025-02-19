from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChangePasswordView, ForgotPasswordView, SignUpAPIView, SignInAPIView, UpdateUserProfileView, UserDetailView, VerifyResetCodeView,get_user_points ,LocationViewSet , get_commune_top_users



urlpatterns = [
    # Existing URLs...
    path('users/sign-up/', SignUpAPIView.as_view(), name='inscription'),
    path('users/sign-in/', SignInAPIView.as_view(), name='connexion'),
    path('users/profile/', UserDetailView.as_view(), name='information_profile'),
    path('users/points/', get_user_points, name='get_user_points'),
    path('commune/top-users/', get_commune_top_users, name='commune-top-users'),
    path('departments/', LocationViewSet.as_view({'get': 'list_departments'}), 
         name='departments'),
    path('departments/<str:department_code>/communes/', 
         LocationViewSet.as_view({'get': 'list_communes'}), 
         name='communes'),
    
    # New URLs for updating profile and password
    path('users/profile/update/', UpdateUserProfileView.as_view(), name='update_profile'),
    path('users/profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('users/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('users/verify-reset-code/', VerifyResetCodeView.as_view(), name='verify_reset_code'),
]