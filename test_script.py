import requests

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
                ecoscore_grade = product.get('ecoscore_grade', "Non spécifié")
                ecoscore_score = product.get('ecoscore_score', "Non spécifié")
                co2_total = product.get('ecoscore_data', {}).get('agribalyse', {}).get('co2_total', "Non spécifié")
                agribalyse_code = product.get('ecoscore_data', {}).get('agribalyse', {}).get('agribalyse_proxy_food_code', "Non spécifié")
                
                # Retour des informations enrichies
                return {
                    'name': product.get('product_name', "Nom indisponible"),
                    'category': categories,
                    'brand': product.get('brands', "Marque indisponible"),
                    'image_url': product.get('image_url', ""),
                    'packaging': packaging,
                    'packaging_materials': packaging_materials,
                    'recycling_tags': recycling_tags,
                    'labels': labels,
                    'recyclable': "en:recycle" in recycling_tags or any(label in labels for label in ["en:green-dot", "fr:triman"]),
                    'ecoscore_grade': ecoscore_grade,
                    'ecoscore_score': ecoscore_score,
                    'co2_total': co2_total,
                    'agribalyse_code': agribalyse_code
                }
        except requests.exceptions.JSONDecodeError:
            print("Erreur : La réponse de l'API n'est pas au format JSON valide.")
    
    print(f"Erreur : Impossible de récupérer les données pour le code-barres {barcode}.")
    return None



def map_category_to_recycling_type(category, packaging="", packaging_materials=[], recycling_tags=[], ecoscore_grade=None, co2_total=None):
    """
    Mappe une catégorie ou emballage à un type de poubelle spécifique.
    """
    category = category.lower()
    packaging = packaging.lower()

    # Définir les types de poubelles
    bins = [
        ("Verte", "Verre (sans bouchons ni couvercles)"),
        ("Jaune", "Plastique, carton et emballages"),
        ("Bleue", "Papier et journaux"),
        ("Rouge", "Métal"),
        ("Noire", "Déchets ménagers classiques"),
        ("Marron", "Biodéchets"),
        ("Déchets spéciaux", "Piles, électroniques et déchets dangereux"),
        ("Autre", "Non catégorisé")
    ]

    # Vérre
    if any(keyword in category + packaging for keyword in [
        "verre", "bocal", "bouteille en verre", "pot",
        "glass", "jar", "glass bottle", "container", "fr:bocal", "fr:verre"
    ]) or "en:glass" in packaging_materials:
        return bins[0], 4

    # Plastique, carton et emballages
    if any(keyword in category + packaging for keyword in [
        "plastique", "carton", "papier", "emballage", "bouteille", "canette", "alu", "aluminium",
        "plastic", "cardboard", "paper", "packaging", "bottle", "can", "aluminum",
        "card-box", "pet-bottle", "mixed plastic-bag", "fr:sac plastique", "fr:bouteille en pet",
        "fr:carton plastique" , "étui"
    ]) or any(material in packaging_materials for material in [
        "en:plastic", "en:pet-1-polyethylene-terephthalate", "en:cardboard"
    ]):
        return bins[1], 5

    # Papier et journaux
    if any(keyword in category + packaging for keyword in [
        "papier", "journaux", "prospectus", "annuaires",
        "paper", "newspaper", "brochures", "fr:papier", "fr:prospectus"
    ]):
        return bins[2], 6

    # Métal
    if any(keyword in category + packaging for keyword in [
        "metal", "aluminium", "can", "boîte métal", "steel-can",
        "aluminum", "drink can", "fr:canette métal recyclabbe à l'infini",
        "fr:cannette aluminium", "fr:boîte métal à recycler", "fr:boîte en métal"
    ]) or "en:aluminium" in packaging_materials:
        return bins[3], 6

    # Biodéchets
    if any(keyword in category + packaging for keyword in [
        "organique", "compost", "déchets alimentaires", "épluchures",
        "organic", "food waste", "compostable", "kitchen waste", "peelings",
        "fr:compost", "fr:épluchures", "fr:organique"
    ]):
        return bins[5], 7

    # Déchets ménagers classiques
    if any(keyword in category + packaging for keyword in [
        "ordures ménagères", "non recyclable", "déchet général", "restes",
        "household waste", "non-recyclable", "general waste", "leftovers",
        "fr:non recyclable", "fr:restes", "fr:ordures ménagères"
    ]):
        return bins[4], 3

    # Déchets spéciaux
    if any(keyword in category + packaging for keyword in [
        "pile", "batterie", "électronique", "électroménager", "téléphone", "ordinateur", "déchet dangereux",
        "battery", "electronics", "appliance", "phone", "computer", "hazardous waste",
        "fr:pile", "fr:électronique", "fr:batterie", "fr:déchets dangereux"
    ]):
        return bins[6], 10

    # Analyse supplémentaire avec ecoscore et co2_total
    if ecoscore_grade and ecoscore_grade.lower() in ['a', 'b']:
        return bins[1], 6  # Encourage le recyclage des produits écologiques

    # Par défaut
    return bins[7], 1


# Exemple d'utilisation
#barcode = "8002270116544"  # Code-barres d'exemple
#barcode = "5449000000996"  # Code-barres d'exemple
#barcode = "3254381026402"  # Code-barres d'exemple
#barcode = "3596690775658"  # Code-barres d'exemple
#barcode = "3266980033613"  # Code-barres d'exemple
barcode = "3017620425035"  # Code-barres d'exemple
result = fetch_from_openfoodfacts(barcode)
print(result)
bin = map_category_to_recycling_type(result.get('category',""), result.get("packaging",""), result.get("packaging_materials",""), result.get("labels",""))
print(bin)
#
## Liste de 30 codes-barres à tester
#barcodes = [
#    "3274080005003", "7622210449283", "3017620425035", "3175680011480", "5449000214911",
#    "3017620422003", "5449000000996", "50184453", "3268840001008", "3451080155161",
#    "20724696", "3068320123264", "3225350000501", "3608580065340", "3760020507350"
#]
## Fonction existante pour récupérer les données
#def fetch_from_openfoodfacts_v2(barcode):
#    """
#    Appelle l'API OpenFoodFacts pour obtenir des données enrichies sur un produit.
#    """
#    api_url = f"https://world.openfoodfacts.org/api/v3/product/{barcode}.json"
#    response = requests.get(api_url)
#
#    if response.status_code == 200:
#        try:
#            data = response.json()
#            if data.get('status') == 'success':  # Produit trouvé
#                product = data['product']
#                ecoscore_grade = product.get('ecoscore_grade', "Non spécifié")
#                ecoscore_score = product.get('ecoscore_score', "Non spécifié")
#                
#                # Retourner les données pertinentes
#                return {
#                    'barcode': barcode,
#                    'name': product.get('product_name', "Nom indisponible"),
#                    'ecoscore_grade': ecoscore_grade,
#                    'ecoscore_score': ecoscore_score,
#                }
#        except requests.exceptions.JSONDecodeError:
#            print(f"Erreur : Réponse non valide pour le code-barres {barcode}.")
#    
#    return {'barcode': barcode, 'name': "Produit introuvable", 'ecoscore_grade': "Non spécifié", 'ecoscore_score': "Non spécifié"}
## Tester avec les 30 codes-barres
#def test_ecoscore(barcodes):
#    results = []
#    for barcode in barcodes:
#        result = fetch_from_openfoodfacts_v2(barcode)
#        results.append(result)
#        print(f"Produit : {result['name']}, Code-barres : {result['barcode']}, Écoscore : {result['ecoscore_grade']}, Score : {result['ecoscore_score']}")
#    
#    # Statistiques sur l'écoscore
#    valid_ecoscore = [r for r in results if r['ecoscore_grade'] != "Non spécifié"]
#    invalid_ecoscore = [r for r in results if r['ecoscore_grade'] == "Non spécifié"]
#
#    print("\nRésultats finaux :")
#    print(f"- Nombre de produits avec un écoscore valide : {len(valid_ecoscore)} / {len(barcodes)}")
#    print(f"- Nombre de produits sans écoscore : {len(invalid_ecoscore)} / {len(barcodes)}")
#
#    return results
#
#test_ecoscore(barcodes)