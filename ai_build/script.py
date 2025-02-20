import os
import shutil
import uuid

# Define the paths
SOURCE_DIR = "images/"  # Path to dataset
DEST_DIR = "data/images/"  # Destination folder for restructured dataset

# Mapping of categories to waste bins
CATEGORY_MAPPING = {
    "aerosol_cans": "special",
    "aluminum_food_cans": "rouge",
    "aluminum_soda_cans": "rouge",
    "batteries": "special",
    "cardboard_boxes": "bleue",
    "cardboard_packaging": "bleue",
    "clothing": "noire",
    "coffee_grounds": "marron",
    "disposable_plastic_cutlery": "noire",
    "eggshells": "marron",
    "food_waste": "marron",
    "glass_beverage_bottles": "verte",
    "glass_cosmetic_containers": "verte",
    "glass_food_jars": "verte",
    "magazines": "bleue",
    "newspaper": "bleue",
    "office_paper": "bleue",
    "paper_cups": "bleue",
    "plastic_cup_lids": "jaune",
    "plastic_detergent_bottles": "jaune",
    "plastic_food_containers": "jaune",
    "plastic_shopping_bags": "jaune",
    "plastic_soda_bottles": "jaune",
    "plastic_straws": "jaune",
    "plastic_trash_bags": "jaune",
    "plastic_water_bottles": "jaune",
    "shoes": "noire",
    "steel_food_cans": "rouge",
    "styrofoam_cups": "noire",
    "styrofoam_food_containers": "noire",
    "tea_bags": "marron"
}

# Ensure destination folders exist
for bin_name in set(CATEGORY_MAPPING.values()):
    os.makedirs(os.path.join(DEST_DIR, bin_name), exist_ok=True)

# Move files into their new category bins with unique names
for category, bin_color in CATEGORY_MAPPING.items():
    category_path = os.path.join(SOURCE_DIR, category)

    if os.path.exists(category_path):
        for subfolder in ["default", "real_world"]:
            subfolder_path = os.path.join(category_path, subfolder)
            
            if os.path.exists(subfolder_path):
                for file in os.listdir(subfolder_path):
                    file_path = os.path.join(subfolder_path, file)

                    # Ensure it's a file
                    if os.path.isfile(file_path):
                        # Generate a unique filename to prevent overwriting
                        file_extension = os.path.splitext(file)[1]
                        unique_filename = f"{category}_{uuid.uuid4().hex[:8]}{file_extension}"

                        new_path = os.path.join(DEST_DIR, bin_color, unique_filename)
                        shutil.move(file_path, new_path)
                        print(f"Moved {file_path} → {new_path}")

print("✅ Dataset restructuring complete!")
