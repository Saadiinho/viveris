def map_category_to_recycling_type(category):
    """
    Mappe une catégorie API (en français ou anglais) à un type de déchet spécifique.
    """
    category = category.lower()

    # Recyclables (emballages, papier/carton)
    if any(keyword in category for keyword in [
        "plastique", "carton", "papier", "emballage", "bouteille", "canette", "alu", "aluminium",
        "plastic", "cardboard", "paper", "packaging", "bottle", "can", "aluminum"
    ]):
        return "Recyclables"

    # Compost (déchets organiques)
    elif any(keyword in category for keyword in [
        "organique", "alimentaire", "compost", "déchet de cuisine", "fruits", "légumes", "épluchures",
        "organic", "food waste", "compostable", "kitchen waste", "fruits", "vegetables", "peelings"
    ]):
        return "Compost"

    # Verre
    elif any(keyword in category for keyword in [
        "verre", "bocal", "bouteille en verre", "pot",
        "glass", "jar", "glass bottle", "container"
    ]):
        return "Verre"

    # Ordures ménagères
    elif any(keyword in category for keyword in [
        "ordures ménagères", "non recyclable", "déchet général", "restes",
        "household waste", "non-recyclable", "general waste", "leftovers"
    ]):
        return "Ordures ménagères"

    # Déchets spéciaux (piles, électronique)
    elif any(keyword in category for keyword in [
        "pile", "batterie", "électronique", "électroménager", "téléphone", "ordinateur", "déchet dangereux",
        "battery", "electronics", "appliance", "phone", "computer", "hazardous waste"
    ]):
        return "Déchets spéciaux"

    # Par défaut, catégorie inconnue
    return "Autre"
