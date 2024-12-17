from rest_framework import serializers
from .models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='formatted_phone', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'commune']

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'phone', 'commune']

    def create(self, validated_data):
        # Crée un utilisateur avec un mot de passe sécurisé
        user = user = User.objects.create_user(
            username=validated_data['email'],  # Le username est remplacé par l'email
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            commune=validated_data['commune']
        )
        return user
    

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Cet email n'est pas enregistré.")
        return value
