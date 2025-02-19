from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ChangePasswordSerializer, SignUpSerializer, SignInSerializer, UpdateUserSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from rest_framework import viewsets, status
from rest_framework.decorators import action
import requests
from rest_framework.permissions import AllowAny

class LocationViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list_departments(self, request):
        """Get all French departments"""
        response = requests.get("https://geo.api.gouv.fr/departements")
        if response.status_code == 200:
            departments = response.json()
            return Response({
                "status": "success",
                "data": departments
            })
        return Response({
            "status": "error",
            "message": "Impossible de récupérer les départements"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def list_communes(self, request, department_code):
        """Get communes for a specific department"""
        response = requests.get(
            f"https://geo.api.gouv.fr/departements/{department_code}/communes"
        )
        if response.status_code == 200:
            communes = response.json()
            return Response({
                "status": "success",
                "data": communes
            })
        return Response({
            "status": "error",
            "message": "Impossible de récupérer les communes"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class SignUpAPIView(APIView):
 def post(self, request):
    serializer = SignUpSerializer(data=request.data)
    if not serializer.is_valid():
        print("Validation errors:", serializer.errors)  # Print validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():
        user = serializer.save() # create user after validation
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        return Response({
            "message": "Utilisateur créé avec succès",
            "access": access_token,
            "refresh": refresh_token,
            "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "commune": user.commune
            }
        }, status=status.HTTP_201_CREATED)
    # If invalid, return errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
User = get_user_model()

class SignInAPIView(APIView):
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "Identifiants invalides"}, status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            return Response({"detail": "Identifiants invalides"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Assure que seul l'utilisateur connecté peut accéder à cette vue

    def get(self, request):
        user = request.user  # Récupère l'utilisateur connecté
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    
from rest_framework.decorators import api_view, permission_classes

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_points(request):
    """
    Returns the current user's total points.
    """
    return Response({"total_points": request.user.total_points}, status=status.HTTP_200_OK)


class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Profil mis à jour avec succès",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "commune": user.commune
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            
            # Generate new tokens after password change
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Mot de passe changé avec succès",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_commune_top_users(request):
    user_commune = request.user.commune
    
    if not user_commune:
        return Response({
            "error": "Vous devez être associé à une commune"
        }, status=400)
        
    top_users = User.objects.filter(
        commune=user_commune
    ).order_by('-total_points')[:5]
    
    return Response({
        "commune": user_commune,
        "top_users": [
            {
                "avatar_name": user.avatar_name,
                "total_points": user.total_points,
                "rank": index + 1
            }
            for index, user in enumerate(top_users)
        ]
    })