from django.db import models
from django.contrib.auth.models import AbstractUser
# models.py
import random
from django.utils import timezone


class User(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)
    commune = models.CharField(max_length=100, null=True, blank=True)
    total_points = models.IntegerField(default=0)
    avatar_name = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Added null=True

    # Lists for generating avatar names
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

    def save(self, *args, **kwargs):
        if not self.avatar_name:
            self.avatar_name = self.generate_avatar_name()
        super().save(*args, **kwargs)

    def generate_avatar_name(self):
        # Try to generate a unique name (max 10 attempts)
        for _ in range(10):
            adj = random.choice(self.ADJECTIVES)
            noun = random.choice(self.NOUNS)
            number = random.randint(1, 999)
            avatar_name = f"{adj}{noun}{number}"
            
            # Check if this name is already taken
            if not User.objects.filter(avatar_name=avatar_name).exists():
                return avatar_name

        # If we couldn't generate a unique name after 10 attempts,
        # use timestamp to ensure uniqueness
        timestamp = int(timezone.now().timestamp())
        return f"{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}{timestamp}"

    def get_public_profile(self):
        """Return public profile information"""
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