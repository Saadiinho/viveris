import json
from django.shortcuts import render
import requests
from django.http import JsonResponse
from .models import Product
import logging
from django.views.decorators.csrf import csrf_exempt
logger = logging.getLogger(__name__)

# Remplacez par votre clé API Barcode Lookup
BARCODE_LOOKUP_API_KEY = "m2cix88kkoh9k07wyjhgscoubwmxlm"

def map_category_to_recycling_type(category, packaging=""):
    """
    Mappe une catégorie ou emballage à un type de déchet spécifique.
    """
    category = category.lower()
    packaging = packaging.lower()

    # Recyclables (emballages, papier/carton)
    if any(keyword in category + packaging for keyword in [
        "plastique", "carton", "papier", "emballage", "bouteille", "canette", "alu", "aluminium",
        "plastic", "cardboard", "paper", "packaging", "bottle", "can", "aluminum",
        "card-box", "pet-bottle", "mixed plastic-bag", "fr:sac plastique", "fr:bouteille en pet",
        "fr:carton plastique"
    ]):
        return "Recyclables"

    # Compost (déchets organiques)
    elif any(keyword in category + packaging for keyword in [
        "organique", "alimentaire", "compost", "déchet de cuisine", "fruits", "légumes", "épluchures",
        "organic", "food waste", "compostable", "kitchen waste", "fruits", "vegetables", "peelings",
        "fr:compost", "fr:épluchures", "fr:organique"
    ]):
        return "Compost"

    # Verre
    elif any(keyword in category + packaging for keyword in [
        "verre", "bocal", "bouteille en verre", "pot",
        "glass", "jar", "glass bottle", "container", "film", "wrapper",
        "fr:bocal", "fr:film", "fr:verre", "fr:pot"
    ]):
        return "Verre"

    # Métal
    elif any(keyword in category + packaging for keyword in [
        "metal", "can", "drink can", "canned", "steel-can", "fr:canette métal recyclabbe à l'infini",
        "fr:cannette aluminium", "fr:boîte métal à recycler", "fr:boîte en métal"
    ]):
        return "Métal"

    # Ordures ménagères
    elif any(keyword in category + packaging for keyword in [
        "ordures ménagères", "non recyclable", "déchet général", "restes",
        "household waste", "non-recyclable", "general waste", "leftovers",
        "fr:non recyclable", "fr:restes", "fr:ordures ménagères"
    ]):
        return "Ordures ménagères"

    # Déchets spéciaux (piles, électronique)
    elif any(keyword in category + packaging for keyword in [
        "pile", "batterie", "électronique", "électroménager", "téléphone", "ordinateur", "déchet dangereux",
        "battery", "electronics", "appliance", "phone", "computer", "hazardous waste",
        "fr:pile", "fr:électronique", "fr:batterie", "fr:déchets dangereux"
    ]):
        return "Déchets spéciaux"

    # Par défaut, catégorie inconnue
    return "Autre"

def fetch_from_openfoodfacts(barcode):
    """
    Appelle l'API OpenFoodFacts pour obtenir des données sur un produit.
    """
    api_url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 1:  # Produit trouvé
            product = data['product']
            return {
                'name': product.get('product_name', "Nom indisponible"),
                'category': product.get('categories', "Catégorie indisponible"),
                'brand': product.get('brands', "Marque indisponible"),
                'image_url': product.get('image_url', ""),
                'packaging': product.get('packaging', "")  # Utiliser pour la catégorisation
            }
    return None

def fetch_from_barcodelookup(barcode):
    """
    Appelle l'API Barcode Lookup pour obtenir des données sur un produit.
    """
    api_url = f"https://api.barcodelookup.com/v3/products?barcode={barcode}&key={BARCODE_LOOKUP_API_KEY}"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if data.get('products'):
            product_data = data['products'][0]
            return {
                'name': product_data.get("product_name", "Nom indisponible"),
                'category': product_data.get("category", "Catégorie indisponible"),
                'brand': product_data.get("brand", "Marque indisponible"),
                'image_url': product_data.get("images", [""])[0]
            }
    return None

def scan_page(request):
    """
    Vue pour rendre la page HTML avec l'interface de scan.
    """
    return render(request, 'scanner/scan.html')

@csrf_exempt
def scan_barcode(request):
    """
    Vue pour traiter les requêtes POST contenant un code-barres dans le body JSON.
    Exemple de body: { "barcode": "3268840001008" }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    # Parse JSON body to extract 'barcode'
    try:
        body = json.loads(request.body)
        barcode = body.get('barcode', None) 
    except:
        return JsonResponse({'error': 'No valid JSON body'}, status=400)

    if not barcode:
        return JsonResponse({'error': 'No barcode provided'}, status=400)

    logger.info(f"Requête reçue avec le code-barres : {barcode}")

    # Vérifier si le produit existe déjà dans la base locale
    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'image_url': product.image_url,
            'recycling_type': product.recycling_type
        })
    except Product.DoesNotExist:
        pass

    # Rechercher d'abord dans OpenFoodFacts
    product_data = fetch_from_openfoodfacts(barcode)
    if product_data:
        recycling_type = map_category_to_recycling_type(
            product_data.get("category", ""),
            product_data.get("packaging", "")
        )
        product = Product.objects.create(
            barcode=barcode,
            name=product_data.get("name"),
            category=product_data.get("category"),
            brand=product_data.get("brand"),
            image_url=product_data.get("image_url"),
            recycling_type=recycling_type
        )
        return JsonResponse({
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'image_url': product.image_url,
            'recycling_type': product.recycling_type
        })

    # Si non trouvé, chercher dans Barcode Lookup
    product_data = fetch_from_barcodelookup(barcode)
    if product_data:
        recycling_type = map_category_to_recycling_type(product_data.get("category", ""))
        product = Product.objects.create(
            barcode=barcode,
            name=product_data.get("name"),
            category=product_data.get("category"),
            brand=product_data.get("brand"),
            image_url=product_data.get("image_url"),
            recycling_type=recycling_type
        )
        return JsonResponse({
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'image_url': product.image_url,
            'recycling_type': product.recycling_type
        })

    return JsonResponse({'error': 'Produit non trouvé dans aucune API'}, status=404)