import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

# Load your trained model
model2 = tf.keras.models.load_model(
    "/Users/marksalloum/Polytech/ProjetViveris/backend/ai_test/fine_tuned_resnet50.keras"
)
print(model2.summary())

# List of classes in order of training
class_names = ['aerosol_cans', 'aluminum_food_cans', 'aluminum_soda_cans', 'cardboard_boxes', 'cardboard_packaging', 'clothing', 'coffee_grounds', 'disposable_plastic_cutlery', 'eggshells', 'food_waste', 'glass_beverage_bottles', 'glass_cosmetic_containers', 'glass_food_jars', 'magazines', 'newspaper', 'office_paper', 'paper_cups', 'plastic_cup_lids', 'plastic_detergent_bottles', 'plastic_food_containers', 'plastic_shopping_bags', 'plastic_soda_bottles', 'plastic_straws', 'plastic_trash_bags', 'plastic_water_bottles', 'shoes', 'steel_food_cans', 'styrofoam_cups', 'styrofoam_food_containers', 'tea_bags']

def load_and_preprocess_image(img_path, img_size=(224, 224)):
    img = tf.io.read_file(img_path)
    img = tf.io.decode_image(img, channels=3)
    img = tf.image.resize(img, img_size)
    # Use ResNet50's built-in preprocessing
    img = tf.keras.applications.resnet50.preprocess_input(img)
    # Add batch dimension
    img = tf.expand_dims(img, axis=0)
    return img

def predict_image(img_path, confidence_threshold=0.7):
    """
    Predict the class of an image with a confidence threshold.
    
    Args:
        img_path (str): Path to the image.
        confidence_threshold (float): Minimum confidence required to accept a prediction.
    
    Returns:
        None
    """
    # Preprocess the image
    img_tensor = load_and_preprocess_image(img_path)

    # Make a prediction
    predictions = model2.predict(img_tensor)  # shape = (1, nb_classes)
    predicted_class_index = np.argmax(predictions[0])  # Get the class with the highest score
    confidence_score = predictions[0][predicted_class_index]  # Confidence of the predicted class

    # Check if confidence meets the threshold
    if confidence_score >= confidence_threshold:
        predicted_class = class_names[predicted_class_index]
        print(f"Image: {img_path}")
        print(f"Predicted Class: {predicted_class}")
        print(f"Confidence Score: {confidence_score:.2f}\n")

        # Display the image with prediction
        plt.imshow(tf.squeeze(img_tensor))  # Remove batch dimension
        plt.title(f"Class: {predicted_class} ({confidence_score:.2f})")
        plt.axis("off")
        plt.show()
    else:
        print(f"Image: {img_path}")
        print(f"Low confidence ({confidence_score:.2f}). Unable to classify reliably.\n")
        plt.imshow(tf.squeeze(img_tensor))
        plt.title(f"Low Confidence: {confidence_score:.2f}")
        plt.axis("off")
        plt.show()

# Example usage
if __name__ == "__main__":
    # Replace with the path of an image you want to predict
    chemin_image = "/Users/marksalloum/Polytech/ProjetViveris/backend/ai_test/image.png"
    predict_image(chemin_image, confidence_threshold=0.7)
