from rest_framework import serializers
from .models import WasteClassification

class WasteClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteClassification
        fields = ['id', 'image', 'predicted_class', 'confidence_score', 
                 'bin_score', 'product_type', 'created_at']

class WasteClassificationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    predicted_class = serializers.CharField(allow_null=True)
    confidence_score = serializers.FloatField(allow_null=True)
    bin_score = serializers.IntegerField(allow_null=True)
    product_type = serializers.CharField()
    image_url = serializers.URLField(allow_null=True)
    all_scores = serializers.DictField(child=serializers.FloatField(), allow_null=True)
    error = serializers.CharField(allow_null=True)