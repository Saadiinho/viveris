from django.db import models

class WasteClassification(models.Model):
    image = models.ImageField(upload_to='waste_classifications/')
    predicted_class = models.CharField(max_length=50)
    confidence_score = models.FloatField()
    bin_score = models.IntegerField(default=1)  # Default score of 1 for unknown/unclassified items
    product_type = models.CharField(max_length=100, default="Unknown Product Type")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product_type} - {self.predicted_class} ({self.confidence_score:.2f})"