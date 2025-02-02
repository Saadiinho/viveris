import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore
import os
from django.conf import settings

class WasteClassifier:
    def __init__(self):
        # Load the model when initializing the class
        model_path = os.path.join(settings.BASE_DIR, 'model', 'fine_tuned_resnet50.keras')
        self.model = tf.keras.models.load_model(model_path)
        
        # Define class names
        self.class_names = ['bleue', 'jaune', 'marron', 'noire', 'rouge', 'special', 'verte']
        
    def load_and_preprocess_image(self, image_file, img_size=(224, 224)):
        """
        Load and preprocess an image file for prediction
        """
        # Read the image file into a tensor
        img_bytes = image_file.read()
        img = tf.io.decode_image(img_bytes, channels=3)
        
        # Resize the image
        img = tf.image.resize(img, img_size)
        
        # Preprocess the image for ResNet50
        img = preprocess_input(img)
        
        # Add batch dimension
        img = tf.expand_dims(img, axis=0)
        return img

    def predict_image(self, image_file, confidence_threshold=0.7):
        """
        Predict the waste category for an uploaded image and return all class scores.
        """
        try:
            # Preprocess the image
            img_tensor = self.load_and_preprocess_image(image_file)
            
            # Make prediction
            predictions = self.model.predict(img_tensor)[0]  # Extract first batch prediction
            
            # Get all confidence scores
            confidence_scores = {self.class_names[i]: float(score) for i, score in enumerate(predictions)}
            print(confidence_scores)
            
            # Get top predicted class
            predicted_class_index = np.argmax(predictions)
            confidence_score = float(predictions[predicted_class_index])
            
            # Check confidence threshold
            if confidence_score >= confidence_threshold:
                predicted_class = self.class_names[predicted_class_index]
                # Get the bin score and product type
                bin_score = get_bin_score(predicted_class)
                product_type = get_product_type(predicted_class)
                
                return {
                    'success': True,
                    'predicted_class': predicted_class,
                    'confidence_score': confidence_score,
                    'all_scores': confidence_scores,
                    'bin_score': bin_score,
                    'product_type': product_type,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'predicted_class': None,
                    'confidence_score': confidence_score,
                    'all_scores': confidence_scores,
                    'bin_score': None,
                    'product_type': get_product_type("unknown"),
                    'error': 'Low confidence prediction'
                }
                
        except Exception as e:
            return {
                'success': False,
                'predicted_class': None,
                'confidence_score': None,
                'all_scores': None,
                'bin_score': None,
                'product_type': get_product_type("unknown"),
                'error': str(e)
            }


##################################################################
# HELPER FUNCTIONS
##################################################################
def get_bin_score(bin_color: str) -> int:
    """
    Convert bin color to a numerical score based on recyclability.
    """
    scoring_system = {
        'verte': 4,    # Glass is highly recyclable
        'jaune': 2,    # Plastic/cardboard
        'bleue': 3,    # Paper
        'rouge': 6,    # Metal
        'noire': 3,    # General waste
        'marron': 6,   # Organic waste
        'special': 10, # Special/hazardous
    }
    return scoring_system.get(bin_color, 1)

def get_product_type(bin_color: str) -> str:
    if bin_color == "unknown":
        return "Unknown Product Type"
    product_types = {
        'verte': "Glass Product",
        'jaune': "Mixed Recyclable Product",
        'bleue': "Paper Product",
        'rouge': "Metal Product",
        'noire': "Non-Recyclable Product",
        'marron': "Organic Product",
        'special': "Hazardous/Special Product"
    }
    return product_types.get(bin_color, "Unknown Product Type")

# Create a singleton instance
waste_classifier = WasteClassifier()