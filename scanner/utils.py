from collections import Counter
from typing import List, Tuple, Dict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from enum import Enum

class Language(Enum):
    EN = 'en'
    FR = 'fr'

class WasteClassifier:
    def __init__(self):
        """Initialize the multilingual waste classifier with prougeefined rules and weights."""
        # Download requirouge NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            print("Note: NLTK data might not be completely downloaded. The classifier will still work.")
        
        # Define bin categories with multilingual descriptions and keywords
        self.bin_categories = {
            'verte': {
                'description': {
                    'en': "Glass (without caps or lids)",
                    'fr': "Verre (sans bouchons ni couvercles)"
                },
                'keywords': {
                    'en': ["glass", "jar", "glass bottle", "container", "wine bottle", "glass container"],
                    'fr': ["verre", "bocal", "bouteille en verre", "pot", "bouteille de vin"]
                },
                'weight': 1.0,
                'incompatible_materials': ['plastic', 'plastique', 'metal', 'métal']
            },
            'jaune': {
                'description': {
                    'en': "Plastic, cardboard and packaging",
                    'fr': "Plastique, carton et emballages"
                },
                'keywords': {
                    'en': ["plastic", "cardboard", "packaging", "bottle", "container", "wrapper", "box"],
                    'fr': ["plastique", "carton", "emballage", "bouteille", "conteneur", "boîte"]
                },
                'weight': 0.8,
                'incompatible_materials': []
            },
            'bleue': {
                'description': {
                    'en': "Paper and newspapers",
                    'fr': "Papier et journaux"
                },
                'keywords': {
                    'en': ["paper", "newspaper", "magazine", "brochure", "flyer", "mail", "envelope"],
                    'fr': ["papier", "journal", "magazine", "prospectus", "publicité", "courrier"]
                },
                'weight': 0.7,
                'incompatible_materials': ['plastic', 'plastique', 'metal', 'métal']
            },
            'rouge': {
                'description': {
                    'en': "Metal",
                    'fr': "Métal"
                },
                'keywords': {
                    'en': ["metal", "aluminum", "tin", "can", "metal box", "steel"],
                    'fr': ["métal", "aluminium", "conserve", "boîte métal", "acier"]
                },
                'weight': 0.9,
                'incompatible_materials': []
            },
            'noire': {
                'description': {
                    'en': "General household waste",
                    'fr': "Déchets ménagers classiques"
                },
                'keywords': {
                    'en': ["household waste", "general waste", "non-recyclable", "trash", "garbage"],
                    'fr': ["ordures ménagères", "déchets généraux", "non recyclable", "poubelle"]
                },
                'weight': 0.3,
                'incompatible_materials': []
            },
            'marron': {
                'description': {
                    'en': "Organic waste",
                    'fr': "Biodéchets"
                },
                'keywords': {
                    'en': ["organic", "food waste", "compost", "vegetable", "fruit", "garden waste"],
                    'fr': ["organique", "déchets alimentaires", "compost", "légume", "fruit"]
                },
                'weight': 0.9,
                'incompatible_materials': ['plastic', 'plastique', 'metal', 'métal', 'glass', 'verre']
            },
            'special': {
                'description': {
                    'en': "Special waste (batteries, electronics, hazardous)",
                    'fr': "Déchets spéciaux (piles, électroniques, dangereux)"
                },
                'keywords': {
                    'en': ["battery", "electronic", "hazardous", "chemical", "paint", "phone"],
                    'fr': ["pile", "électronique", "dangereux", "chimique", "peinture", "téléphone"]
                },
                'weight': 1.0,
                'incompatible_materials': []
            }
        }
        
        # Multilingual material synonyms
        self.material_synonyms = {
            # English
            'pet': 'plastic',
            'hdpe': 'plastic',
            'ldpe': 'plastic',
            'pp': 'plastic',
            'ps': 'plastic',
            'pvc': 'plastic',
            'aluminum': 'metal',
            'aluminium': 'metal',
            'steel': 'metal',
            'iron': 'metal',
            'tin': 'metal',
            # French
            'plastique': 'plastic',
            'métal': 'metal',
            'aluminium': 'metal',
            'acier': 'metal',
            'fer': 'metal',
            'étain': 'metal',
        }

    def detect_language(self, text: str) -> str:
        """Detect if the text is primarily English or French."""
        fr_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'en', 'bouteille', 'poubelle']
        en_indicators = ['the', 'of', 'in', 'bottle', 'container', 'bin', 'waste']
        
        text_lower = text.lower()
        fr_count = sum(1 for word in fr_indicators if word in text_lower)
        en_count = sum(1 for word in en_indicators if word in text_lower)
        
        return 'fr' if fr_count > en_count else 'en'

    def preprocess_text(self, text: str) -> str:
        """Preprocess text using simple tokenization and stopword removal."""
        # Converte to lowercase
        text = text.lower()
        
        # Choose appropriate stopwords based on detected language
        lang = self.detect_language(text)
        try:
            stop_words = set(stopwords.words('french' if lang == 'fr' else 'english'))
        except:
            stop_words = set()
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [word for word in tokens if word not in stop_words]
        
        return " ".join(tokens)

    # Only showing the modified methods - the rest of the class remains the same

    def _clean_material_string(self, material: str) -> str:
        """
        Clean material string by removing language prefixes and trimming.
        
        Args:
            material (str): Material string possibly with language prefix (e.g., 'en:plastic' or 'fr:plastique')
        
        Returns:
            str: Cleaned material string
        """
        if not material:
            return ""
            
        # Remove language prefix if present
        if material.startswith(('en:', 'fr:')):
            material = material[3:]
        
        return material.strip().lower()
    
    def _adjust_scores_for_combinations(self, scores: Dict[str, float], materials: List[str]) -> None:
        """Adjust scores based on material combinations and special rules."""
        # Standardize materials using synonyms
        std_materials = []
        for material in materials:
            for synonym, std_term in self.material_synonyms.items():
                if synonym in material:
                    std_materials.append(std_term)
                    break
            else:
                std_materials.append(material)

        # Count unique materials
        material_count = Counter(std_materials)
        
        # Apply combination rules
        if len(material_count) > 1:
            if 'plastic' in material_count and 'metal' in material_count:
                scores['jaune'] *= 1.5  # Preference for jaune bin for mixed materials
                scores['rouge'] *= 0.5
            
            if any(glass in material_count for glass in ['glass', 'verre']):
                scores['verte'] *= 0.3  # rougeuce score for glass bin
                scores['noire'] *= 1.5  # Increase score for general waste
        
        # Check for incompatible materials
        for bin_type, config in self.bin_categories.items():
            if any(material in std_materials for material in config['incompatible_materials']):
                scores[bin_type] *= 0.1
    
    def _adjust_scores_for_main_material(self, scores: Dict[str, float], main_material: str) -> None:
        """Adjust scores when a main material is specified."""
        # Standardize the main material using synonyms
        std_main_material = main_material
        for synonym, std_term in self.material_synonyms.items():
            if synonym in main_material:
                std_main_material = std_term
                break
        
        # Boost scores based on main material type
        material_bin_mapping = {
            'plastic': 'jaune',
            'metal': 'rouge',
            'glass': 'verte',
            'paper': 'bleue',
            'organic': 'marron',
            'hazardous': 'special'
        }
        
        # If we have a mapping for this material, heavily boost its score
        if std_main_material in material_bin_mapping:
            target_bin = material_bin_mapping[std_main_material]
            for bin_type in scores:
                if bin_type == target_bin:
                    scores[bin_type] *= 3.0  # Triple the score for the matching bin
                else:
                    scores[bin_type] *= 0.3  # Reduce other scores

    def calculate_material_scores(self, packaging: str, materials: List[str], main_material: str = "") -> Tuple[Dict[str, float], str]:
        """Calculate scores for each bin category based on packaging and materials."""
        # Detect language
        lang = self.detect_language(packaging)
        
        # Preprocess input
        processed_packaging = self.preprocess_text(packaging)
        processed_materials = [self.preprocess_text(self._clean_material_string(m)) for m in materials]
        processed_main = self.preprocess_text(self._clean_material_string(main_material)) if main_material else ""
        
        # If main_material is present, only use that for scoring
        if processed_main:
            combined_text = f"{processed_main}"
        else:
            # Otherwise use all materials
            combined_text = f"{processed_packaging} {' '.join(processed_materials)}"
        
        # Initialize scores
        scores = {bin_type: 0.0 for bin_type in self.bin_categories.keys()}
        
        # Calculate base scores from keywords
        for bin_type, config in self.bin_categories.items():
            # Check keywords in both languages
            keyword_matches = sum(1 for keyword in config['keywords']['en'] + config['keywords']['fr']
                                if keyword in combined_text)
            scores[bin_type] = keyword_matches * config['weight']
        
        # If there's no main material, adjust scores based on combinations
        if not processed_main:
            self._adjust_scores_for_combinations(scores, processed_materials)
        else:
            # If there is a main material, make its score dominant
            self._adjust_scores_for_main_material(scores, processed_main)
        
        return scores, lang



    def classify_waste(self, packaging: str, materials: List[str] = None, main_material: str = "") -> Tuple[str, str, float]:
        """
        Classify waste item into appropriate bin category.
        
        Args:
            packaging (str): The packaging description
            materials (List[str]): List of materials
            main_material (str): The main/primary material (takes precedence if present)
        
        Returns:
            tuple of (bin_color, description, confidence_score)
        """
        materials = materials or []
        
        # Calculate scores and detect language
        scores, lang = self.calculate_material_scores(packaging, materials, main_material)
        
        # Get the bin with highest score
        best_bin = max(scores.items(), key=lambda x: x[1])
        bin_type = best_bin[0]
        confidence = best_bin[1]
        
        # Normalize confidence score to 0-1 range
        max_possible_score = 5.0
        confidence = min(confidence / max_possible_score, 1.0)
        
        return (bin_type, 
                self.bin_categories[bin_type]['description'][lang],
                confidence)

    def explain_classification(self, packaging: str, materials: List[str] = None, main_material: str = "") -> str:
        """Provide detailed explanation for the classification decision."""
        materials = materials or []
        scores, lang = self.calculate_material_scores(packaging, materials, main_material)
        classification = self.classify_waste(packaging, materials, main_material)
        
        if lang == 'fr':
            explanation = [
                f"Résultat de la classification: {classification[0]} (confiance: {classification[2]:.2%})",
                f"Description: {classification[1]}",
            ]
            if main_material:
                explanation.append(f"Matériau principal: {main_material}")
            explanation.append("\nScores par poubelle:")
        else:
            explanation = [
                f"Classification result: {classification[0]} (confidence: {classification[2]:.2%})",
                f"Description: {classification[1]}",
            ]
            if main_material:
                explanation.append(f"Main material: {main_material}")
            explanation.append("\nBin scores:")
        
        for bin_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            explanation.append(f"- {bin_type}: {score:.2f}")
            
        return "\n".join(explanation)

def get_bin_score( bin_color: str) -> int:
    """
    Converte bin color to a numerical score based on recyclability.
    
    Args:
        bin_color (str): The color/type of the bin (e.g., 'verte', 'jaune', etc.)
        
    Returns:
        int: Score value representing recyclability (1-10)
    """
    scoring_system = {
        'verte': 4,      # Glass is highly recyclable
        'jaune': 2,     # Plastic/cardboard mixed recyclables
        'bleue': 3,       # Paper is very recyclable
        'rouge': 6,        # Metal is highly recyclable
        'noire': 3,      # General waste - low score
        'marron': 6,      # Organic waste - good for environment
        'special': 10,   # Special waste needs proper handling
    }
    
    return scoring_system.get(bin_color, 1)  # Default score of 1 if bin color not found

def get_product_type( bin_color: str) -> str:
    """
    Determine the general product type based on the bin color.
    
    Args:
        bin_color (str): The color/type of the bin (e.g., 'verte', 'jaune', etc.)
        
    Returns:
        str: Description of the product type
    """
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

