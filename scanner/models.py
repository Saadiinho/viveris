from django.db import models

from authentication.models import User

class Product(models.Model):
    barcode = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200, null=True, blank=True)
    brand = models.CharField(max_length=200, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    recycling_type = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name or "Produit inconnu"

class UserScore(models.Model):
    user_id = models.CharField(max_length=255, unique=True)  # ID unique pour l'utilisateur
    score = models.IntegerField(default=0)  # Score total

    def __str__(self):
        return f"User {self.user_id} - Score: {self.score}"
    

class Bin(models.Model):
    latitude = models.FloatField()  # Utilisez FloatField pour les coordonnées
    longitude = models.FloatField()  # Corrigez l'orthographe et utilisez FloatField
    types = models.JSONField()  # Utilisez JSONField pour stocker une liste ou un objet JSON
    comment = models.CharField(max_length=255, blank=True, null=True)  # Ajoutez max_length

    def __str__(self):
        return f"Bin at ({self.latitude}, {self.longitude})"


from django.conf import settings  # For referencing the custom User model

class RecyclingActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Or "User" if you imported it directly
        on_delete=models.CASCADE,
        related_name="recycling_activities"
    )
    product_name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    date_scanned = models.DateTimeField(auto_now_add=True)
    points_earned = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product_name} - {self.user.email} ({self.quantity} items)"

