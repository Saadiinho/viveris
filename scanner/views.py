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
from .utils import WasteClassifier, get_bin_score , get_product_type

from .models import Product, Bin, RecyclingActivity
from django.core.exceptions import ObjectDoesNotExist
logger = logging.getLogger(__name__)
classifier = WasteClassifier()

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


def fetch_from_openfoodfacts(barcode):
    """
    Appelle l'API OpenFoodFacts pour obtenir des données enrichies sur un produit.
    """
    api_url = f"https://world.openfoodfacts.org/api/v3/product/{barcode}.json"
    response = requests.get(api_url)

    if response.status_code == 200:
        try:
            data = response.json()
            if data.get('status') == 'success':  # Produit trouvé
                product = data['product']
                # Extraire les données pertinentes
                packaging_materials = product.get('packaging_materials_tags', [])
                recycling_tags = product.get('packaging_recycling_tags', [])
                packaging = product.get('packaging', "Non spécifié")
                labels = product.get('labels_tags', [])
                categories = product.get('categories', "Non spécifié")
                packagings_materials_main = product.get('packagings_materials_main','')
                # Retour des informations enrichies
                return {
                    'name': product.get('product_name', "Nom indisponible"),
                    'category': categories,
                    'brand': product.get('brands', "Marque indisponible"),
                    'image_url': product.get('image_url', ""),
                    'packaging': packaging,
                    'packaging_materials': packaging_materials,
                    'packagings_materials_main' : packagings_materials_main,
                    'recycling_tags': recycling_tags,
                    'labels': labels,
                }
            
        except requests.exceptions.JSONDecodeError:
            print("Erreur : La réponse de l'API n'est pas au format JSON valide.")
    
    print(f"Erreur : Impossible de récupérer les données pour le code-barres {barcode}.")
    return None
    

def scan_page(request):
    """
    Vue pour rendre la page HTML avec l'interface de scan.
    """
    return render(request, 'scanner/scan.html')


@csrf_exempt
def scan_barcode(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        body = json.loads(request.body)
        barcode = body.get('barcode')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    if not barcode:
        return JsonResponse({'error': 'No barcode provided'}, status=400)

    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            'name': product.name,
            'category': product.category,
            'brand': product.brand,
            'image_url': product.image_url,
            'recycling_type': product.recycling_type,
            'recycling_bin': product.recycling_bin,
            'packaging': product.packaging,
            'packaging_materials': product.packaging_materials,
            'packagings_materials_main': product.packagings_materials_main,
            'points': get_bin_score(product.recycling_bin)
        })
    except Product.DoesNotExist:
        logger.info(f"Product with barcode {barcode} not found in local database")

    product_data = fetch_from_openfoodfacts(barcode)
    if product_data:
        try:
            recycling_bin, _ = classifier.classify_waste(
                product_data.get("packaging", ""),
                product_data.get("packaging_materials", []),
                product_data.get("packagings_materials_main", "")
            )

            if recycling_bin == "unknown":
                return JsonResponse({'classification_failed': True}, status=200)

            product = Product.objects.create(
                barcode=barcode,
                name=product_data.get("name"),
                category=product_data.get("category"),
                brand=product_data.get("brand"),
                image_url=product_data.get("image_url"),
                recycling_type=get_product_type(recycling_bin),
                recycling_bin=recycling_bin,
                packaging=product_data.get("packaging", ""),
                packaging_materials=product_data.get("packaging_materials", []),
                packagings_materials_main=product_data.get("packagings_materials_main", ""),
            )

            return JsonResponse({
                'name': product.name,
                'category': product.category,
                'brand': product.brand,
                'image_url': product.image_url,
                'recycling_type': product.recycling_type,
                'recycling_bin': product.recycling_bin,
                'packaging': product.packaging,
                'packaging_materials': product.packaging_materials,
                'packagings_materials_main': product.packagings_materials_main,
                'points': get_bin_score(recycling_bin)
            })
        except Exception as e:
            logger.error(f"Error while processing product: {e}")
            return JsonResponse({'error': 'Failed to process product data'}, status=500)

    return JsonResponse({'error': 'Product not found in any API'}, status=404)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
@csrf_exempt
def user_recycling_activity(request):
    if request.method == "GET":
        activities = RecyclingActivity.objects.filter(user=request.user).order_by('-date_scanned')
        serializer = RecyclingActivitySerializer(activities, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            product_name = body.get("product_name", "")
            product_type = body.get("product_type", "")
            quantity = int(body.get("quantity", 1))
            points_earned= int(body.get("points_earned",1))
            new_activity = RecyclingActivity.objects.create(
                user=request.user,
                product_name=product_name,
                product_type=product_type,
                quantity=quantity,
                points_earned=points_earned,
            )

            request.user.total_points += points_earned
            request.user.save()

            return JsonResponse({
                "message": "Activity created successfully",
                "product_name":product_name,
                "quantity": quantity,
                "activity_id": new_activity.id,
                "points_earned": new_activity.points_earned,
                "product_type": new_activity.product_type,
                "total_points": request.user.total_points,
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)