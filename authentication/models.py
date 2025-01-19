from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)
    commune = models.CharField(max_length=100, null=True, blank=True)

    # NEW FIELD for points
    total_points = models.IntegerField(default=0)

    def formatted_phone(self):
        number = str(self.phone or "")
        if not number:
            return ""
        # Example formatting logic
        formatted_number = f"+33 {number[:1]} {number[1:3]} {number[3:5]} {number[5:7]} {number[7:9]} {number[9:]}"
        return formatted_number

    def __str__(self):
        return self.username
