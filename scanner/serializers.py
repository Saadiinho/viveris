from rest_framework import serializers
from .models import RecyclingActivity
from django.contrib.auth import get_user_model

User = get_user_model()

class RecyclingActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for listing/creating RecyclingActivity.
    """
    class Meta:
        model = RecyclingActivity
        fields = [
            'id', 'user', 'product_name', 'product_type',
            'quantity', 'date_scanned', 'points_earned'
        ]
        read_only_fields = ['user', 'date_scanned', 'points_earned']


