from django.db import models
from django.contrib.auth.models import AbstractUser
import random, string
from django.utils import timezone

class User(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)
    commune = models.CharField(max_length=100, null=True, blank=True)
    total_points = models.IntegerField(default=0)
    
    # Avatar logic
    avatar_name = models.CharField(max_length=50, unique=True, blank=True, null=True)
    ADJECTIVES = [
        "Rapide", "Agile", "Sage", "Malin", "Brave", "Rusé", "Habile",
        "Vigilant", "Vif", "Expert", "Maître", "Héros", "Champion",
        "Fort", "Génial", "Super", "Éco", "Vert", "Bio", "Actif"
    ]
    NOUNS = [
        "Trieur", "Recycleur", "Écolo", "Gardien", "Protecteur", "Défenseur",
        "Guide", "Pionnier", "Aventurier", "Leader", "Expert", "Maestro",
        "Ninja", "Ranger", "Sentinel", "Étoile", "Phoenix", "Dragon", "Tigre",
        "Aigle"
    ]

    # 1) Add a referral_code
    referral_code = models.CharField(
        max_length=10, 
        unique=True, 
        blank=True, 
        null=True
    )

    def save(self, *args, **kwargs):
        # Generate avatar if needed
        if not self.avatar_name:
            self.avatar_name = self.generate_avatar_name()
        
        # 2) Generate referral code if empty
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()

        super().save(*args, **kwargs)

    def generate_avatar_name(self):
        for _ in range(10):
            adj = random.choice(self.ADJECTIVES)
            noun = random.choice(self.NOUNS)
            number = random.randint(1, 999)
            avatar_name = f"{adj}{noun}{number}"
            if not User.objects.filter(avatar_name=avatar_name).exists():
                return avatar_name

        # Fallback
        timestamp = int(timezone.now().timestamp())
        return f"{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}{timestamp}"

    # 3) Code to generate a unique referral code
    def generate_referral_code(self, length=8):
        """Generate a random alphanumeric code and ensure uniqueness."""
        for _ in range(10):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not User.objects.filter(referral_code=code).exists():
                return code

        # Fallback if we can't find a unique code after 10 tries
        return f"{int(timezone.now().timestamp())}"

    def get_public_profile(self):
        return {
            'avatar_name': self.avatar_name,
            'total_points': self.total_points,
            'commune': self.commune
        }

    def __str__(self):
        return self.username or self.email


class Department(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Commune(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='communes')
    zip_code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.name} ({self.zip_code})"
    


import string

class PasswordResetCode(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        """Generate a random 6-digit code"""
        return ''.join(random.choices(string.digits, k=6))

    def is_valid(self):
        """Check if code is still valid (not expired and not used)"""
        expiration_time = timezone.now() - timezone.timedelta(minutes=15)
        return not self.is_used and self.created_at > expiration_time