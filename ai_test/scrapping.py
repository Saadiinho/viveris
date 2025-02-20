import os
import requests
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor
import time
import imghdr

# Configuration - matches your folder structure exactly
BASE_DIR = "/Users/marksalloum/Polytech/ProjetViveris/backend/1/images/images"
CATEGORIES = [
    "plastic_water_bottles",
    "shoes",
    "steel_food_cans",
    "styrofoam_cups",
    "styrofoam_food_containers",
    "tea_bags"
]

MAX_IMAGES = 40  # Per category
NUM_THREADS = 4
REQUEST_DELAY = 1

CATEGORY_QUERIES = {
    "plastic_water_bottles": [
        "disposable plastic water bottle",
        "cristaline water bottle",
        "evian water bottle",
        "vitel water bottle",
    ],
    "shoes": [
        "running shoes on feet",
        "high heels shoes woman",
        "worn sneakers on street",
        "casual shoes on rack",
        "nike shoes display",
        "adidas sneakers collection",
        "converse all star shoes",
    ],
    "steel_food_cans": [
        "campbells soup steel can",
        "baked beans steel can",
        "pet food steel can",
        "tomato puree steel can",
        "heinz beans steel can",
    ],
    "styrofoam_cups": [
        "coffee styrofoam cup",
        "styrofoam cup in fast food",
        "white foam cup polystyrene",
        "takeaway styrofoam cups",
        "dunkin donuts styrofoam cup",
        "mcdonalds foam cup",
    ],
    "styrofoam_food_containers": [
        "takeout styrofoam food box",
        "polystyrene leftover container",
        "foam lunch container",
        "white styrofoam plate container",
        "chinese takeout styrofoam box",
        "fast food polystyrene container",
    ],
    "tea_bags": [
        "lipton tea bag",
        "herbal tea bag green",
        "twinings tea bag earl grey",
        "pg tips tea bag",
        "tetley tea bag",
    ],
}


def download_image(url, path):
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
        if response.status_code == 200 and imghdr.what(None, response.content):
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception as e:
        return False

def process_category(category):
    category_dir = os.path.join(BASE_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    
    existing_files = set(os.listdir(category_dir))
    
    for query in CATEGORY_QUERIES.get(category, [f"{category} product"]):
        query_downloaded = 0  # Track images downloaded for this query
        
        try:
            with DDGS() as ddgs:
                results = ddgs.images(
                    keywords=query,
                    region="wt-wt",
                    safesearch="off",
                    size="Medium",
                    type_image="photo",
                    max_results=MAX_IMAGES
                )
                
                with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                    futures = []
                    for result in results:
                        if query_downloaded >= MAX_IMAGES:
                            break
                        
                        # Create unique filename per query
                        filename = f"{query.replace(' ', '_')}_{query_downloaded + 1}.jpg"
                        filepath = os.path.join(category_dir, filename)
                        
                        if filename not in existing_files:
                            futures.append(executor.submit(
                                download_image, 
                                result['image'], 
                                filepath
                            ))
                            query_downloaded += 1
                            time.sleep(REQUEST_DELAY)
                            
                    for future in futures:
                        future.result()

        except Exception as e:
            print(f"Error in {category} - Query '{query}': {str(e)}")
            continue

if __name__ == "__main__":
    # Create all folders upfront
    for category in CATEGORIES:
        os.makedirs(os.path.join(BASE_DIR, category), exist_ok=True)
    
    # Process all categories
    for category in CATEGORIES:
        print(f"Processing: {category}")
        process_category(category)
    
    print("All images downloaded to correct folders!")
