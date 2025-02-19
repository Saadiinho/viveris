import requests
from rest_framework import serializers
from .models import User
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView


class SignUpSerializer(serializers.ModelSerializer):
    department = serializers.CharField(write_only=True)
    commune = serializers.CharField()
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 
                 'phone', 'department', 'commune']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet e-mail est déjà utilisé.")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value

    def validate(self, data):
        department_code = data.get('department')
        commune_name = data.get('commune')
        
        if not department_code:
            raise serializers.ValidationError({"department": "Le département est requis."})
            
        # Validate department
        dept_response = requests.get(f"https://geo.api.gouv.fr/departements/{department_code}")
        if dept_response.status_code != 200:
            raise serializers.ValidationError({"department": "Code de département invalide."})

        # Validate commune exists in department
        commune_response = requests.get(
            f"https://geo.api.gouv.fr/departements/{department_code}/communes"
        )
        
        if commune_response.status_code != 200:
            raise serializers.ValidationError({"commune": "Impossible de vérifier la commune."})
            
        communes = commune_response.json()
                
        # Case-insensitive comparison
        valid_commune = any(
            c['nom'].lower().strip() == commune_name.lower().strip() 
            for c in communes
        )
        
        if not valid_commune:
            raise serializers.ValidationError(
                {"commune": "Cette commune n'existe pas dans ce département."}
            )

        # Store the exact name from the API
        for c in communes:
            if c['nom'].lower().strip() == commune_name.lower().strip():
                data['commune'] = c['nom']  # Use the official name from API
                break

        return data



    def create(self, validated_data):
        # Remove department as it's not a User model field
        department = validated_data.pop('department')
        # Create user
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone'),
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
    

from .models import Department, Commune

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name']

class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ['id', 'name', 'code', 'zip_code']