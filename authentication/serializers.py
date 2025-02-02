from rest_framework import serializers
from .models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView



class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'phone', 'commune']

    def validate(self, data):
        # 1) Check if an account with this email already exists:
        email = data['email']
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Cet e-mail est déjà utilisé."})

        # 2) If phone is provided, ensure it's unique
        phone = data.get('phone', None)
        if phone:
            if User.objects.filter(phone=phone).exists():
                raise serializers.ValidationError({"phone": "Ce numéro est déjà utilisé."})

        return data

    def create(self, validated_data):
        # Create a user, using email as username
        user = User.objects.create_user(
            username=validated_data['email'],   # for AbstractUser
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', None),
            commune=validated_data.get('commune', None),
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

# auth/serializers.py
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Include total_points if you want to show it in user detail
        fields = ['email', 'first_name', 'last_name', 'phone', 'commune', 'total_points']

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'commune']
        
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.commune = validated_data.get('commune', instance.commune)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Le mot de passe actuel est incorrect.")
        return value