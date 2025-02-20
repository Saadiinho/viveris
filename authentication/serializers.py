# serializers.py
import requests
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    department = serializers.CharField(write_only=True)
    commune = serializers.CharField()
    referral_code = serializers.CharField(
        write_only=True, 
        required=False,  # optional
        allow_blank=True
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 
            'phone', 'department', 'commune',
            'referral_code'
        ]
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
                data['commune'] = c['nom']  # Use official name from API
                break
            
        # Optional: Validate referral_code if provided
        referral_code = data.get('referral_code', None)
        if referral_code:
            referral_code = referral_code.strip()
            if referral_code:
                # Check if the code is valid
                try:
                    referrer = User.objects.get(referral_code=referral_code)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"referral_code": "Code parrain inexistant."})
                # Optionally store the referrer object in the serializer context
                self.context['referrer'] = referrer

        return data

    def create(self, validated_data):
        # Remove department as it's not a User field
        department = validated_data.pop('department')
        referral_code = validated_data.pop('referral_code', None)

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

        # If referral_code was provided and validated, award bonus
        if referral_code and 'referrer' in self.context:
            referrer = self.context['referrer']
            # Award points
            referrer.total_points += 100
            referrer.save()
            user.total_points += 100
            user.save()

        return user

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        # Extract submitted email & password
        email = data.get("email")
        password = data.get("password")

        # 1) Check if a user with this email exists
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": ["Cet email n'est pas enregistré."]})

        # 2) Check if the password is correct
        if not user.check_password(password):
            raise serializers.ValidationError({"password": ["Mot de passe incorrect."]})

        # 3) Optionally check if user is active / not blocked
        if not user.is_active:
            raise serializers.ValidationError({"email": ["Ce compte est désactivé."]})

        # If all checks pass, return the data unmodified
        return data

# auth/serializers.py
from rest_framework import serializers
from .models import PasswordResetCode, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Include total_points if you want to show it in user detail
        fields = ['email', 'first_name', 'last_name', 'phone', 'commune', 'total_points','avatar_name','avatar']

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




class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise serializers.ValidationError("Aucun compte n'est associé à cet email.")
        return value

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError({
                "email": "Aucun compte n'est associé à cet email."
            })

        # Get the latest unused code for this user
        reset_code = PasswordResetCode.objects.filter(
            user=user,
            code=data['code'],
            is_used=False
        ).order_by('-created_at').first()

        if not reset_code:
            raise serializers.ValidationError({
                "code": "Code invalide."
            })

        if not reset_code.is_valid():
            raise serializers.ValidationError({
                "code": "Code expiré. Veuillez demander un nouveau code."
            })

        return data