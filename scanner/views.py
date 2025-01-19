import json
from django.shortcuts import render
import requests
from django.http import JsonResponse

from scanner.serializers import RecyclingActivitySerializer
from .models import Product, Bin
import logging
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from .models import Product, Bin, RecyclingActivity
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)

# Remplacez par votre clé API Barcode Lookup
BARCODE_LOOKUP_API_KEY = "m2cix88kkoh9k07wyjhgscoubwmxlm"

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE"])
def bin_managed(request, bin_id=None):
    """
    Vue pour gérer les poubelles (Ajout, modification, suppression, etc.)
    """
    if request.method == "GET":
        if bin_id:
            # Récupération d'une seule poubelle par ID
            try:
                bin = Bin.objects.get(id=bin_id)
                return JsonResponse({
                    "id": bin.id,
                    "latitude": bin.latitude,
                    "longitude": bin.longitude,
                    "types": bin.types,
                    "comment": bin.comment,
                })
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Bin not found"}, status=404)
        else:
            # Récupération de toutes les poubelles
            bins = Bin.objects.all()
            bins_data = [
                {
                    "id": bin.id,
                    "latitude": bin.latitude,
                    "longitude": bin.longitude,
                    "types": bin.types,
                    "comment": bin.comment,
                }
                for bin in bins
            ]
            return JsonResponse(bins_data, safe=False)

    elif request.method == "POST":
        # Création d'une nouvelle poubelle
        try:
            data = json.loads(request.body)
            bin = Bin.objects.create(
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                types=data.get("types", []),
                comment=data.get("comment", "")
            )
            return JsonResponse({
                "message": "Bin created successfully",
                "id": bin.id,
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "PUT":
        # Mise à jour complète d'une poubelle
        if not bin_id:
            return JsonResponse({"error": "Bin ID is required for update"}, status=400)
        try:
            data = json.loads(request.body)
            bin = Bin.objects.get(id=bin_id)
            bin.latitude = data.get("latitude", bin.latitude)
            bin.longitude = data.get("longitude", bin.longitude)
            bin.types = data.get("types", bin.types)
            bin.comment = data.get("comment", bin.comment)
            bin.save()
            return JsonResponse({"message": "Bin updated successfully"})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Bin not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "PATCH":
        # Mise à jour partielle d'une poubelle
        if not bin_id:
            return JsonResponse({"error": "Bin ID is required for update"}, status=400)
        try:
            data = json.loads(request.body)
            bin = Bin.objects.get(id=bin_id)
            if "latitude" in data:
                bin.latitude = data["latitude"]
            if "longitude" in data:
                bin.longitude = data["longitude"]
            if "types" in data:
                bin.types = data["types"]
            if "comment" in data:
                bin.comment = data["comment"]
            bin.save()
            return JsonResponse({"message": "Bin partially updated successfully"})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Bin not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        # Suppression d'une poubelle
        if not bin_id:
            return JsonResponse({"error": "Bin ID is required for deletion"}, status=400)
        try:
            bin = Bin.objects.get(id=bin_id)
            bin.delete()
            return JsonResponse({"message": "Bin deleted successfully"})
        except ObjectDoesNotExist:
            return JsonResponse({"error": "Bin not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


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



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from .models import Product, Bin, RecyclingActivity
from django.core.exceptions import ObjectDoesNotExist

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])  # Enforces the user must be authenticated
def user_recycling_activity(request):
    """
    GET -> Return all recycling activities for the current user (request.user).
    POST -> Create a new recycling activity and update user points.
    """
    if request.method == "GET":
        activities = RecyclingActivity.objects.filter(user=request.user).order_by('-date_scanned')
        serializer = RecyclingActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        try:
            body = request.data
            product_name = body.get("product_name", "")
            category = body.get("category", "")
            quantity = int(body.get("quantity", 1))

            product_type = map_category_to_recycling_type(category)  # Map category to product type
            points_earned = 10 * quantity  # Example logic: 10 points per item

            # Create the recycling activity
            new_activity = RecyclingActivity.objects.create(
                user=request.user,
                product_name=product_name,
                product_type=product_type,
                quantity=quantity,
                points_earned=points_earned,
            )

            # Update user's total points
            request.user.total_points += points_earned
            request.user.save()

            return Response({
                "message": "Activity created successfully",
                "activity_id": new_activity.id,
                "points_earned": new_activity.points_earned,
                "product_type": new_activity.product_type,
                "total_points": request.user.total_points,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

