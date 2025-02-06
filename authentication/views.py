from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ChangePasswordSerializer, SignUpSerializer, SignInSerializer, UpdateUserSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

class SignUpAPIView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # create user after validation
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