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
        """Initialize the multilingual waste classifier with predefined rules and weights."""
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except:
            print("Note: NLTK data might not be completely downloaded. The classifier will still work.")
        
        # Define bin categories with multilingual descriptions and keywords
        self.bin_categories = {
            'green': {
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
            'yellow': {
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
            'blue': {
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
            'red': {
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
            'black': {
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
            'brown': {
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
        # Convert to lowercase
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

    def calculate_material_scores(self, packaging: str, materials: List[str]) -> Tuple[Dict[str, float], str]:
        """Calculate scores for each bin category based on packaging and materials."""
        # Detect language
        lang = self.detect_language(packaging)
        
        # Preprocess input
        processed_packaging = self.preprocess_text(packaging)
        processed_materials = [self.preprocess_text(m) for m in materials]
        
        # Combine all text for analysis
        combined_text = f"{processed_packaging} {' '.join(processed_materials)}"
        
        # Initialize scores
        scores = {bin_type: 0.0 for bin_type in self.bin_categories.keys()}
        
        # Calculate base scores from keywords
        for bin_type, config in self.bin_categories.items():
            # Check keywords in both languages
            keyword_matches = sum(1 for keyword in config['keywords']['en'] + config['keywords']['fr']
                                if keyword in combined_text)
            scores[bin_type] = keyword_matches * config['weight']
        
        # Adjust scores based on material combinations and rules
        self._adjust_scores_for_combinations(scores, processed_materials)
        
        return scores, lang

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
                scores['yellow'] *= 1.5  # Preference for yellow bin for mixed materials
                scores['red'] *= 0.5
            
            if any(glass in material_count for glass in ['glass', 'verre']):
                scores['green'] *= 0.3  # Reduce score for glass bin
                scores['black'] *= 1.5  # Increase score for general waste
        
        # Check for incompatible materials
        for bin_type, config in self.bin_categories.items():
            if any(material in std_materials for material in config['incompatible_materials']):
                scores[bin_type] *= 0.1

    def classify_waste(self, packaging: str, materials: List[str] = None) -> Tuple[str, str, float]:
        """
        Classify waste item into appropriate bin category.
        Returns tuple of (bin_color, description, confidence_score)
        """
        materials = materials or []
        
        # Calculate scores and detect language
        scores, lang = self.calculate_material_scores(packaging, materials)
        
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

    def explain_classification(self, packaging: str, materials: List[str] = None) -> str:
        """Provide detailed explanation for the classification decision."""
        materials = materials or []
        scores, lang = self.calculate_material_scores(packaging, materials)
        classification = self.classify_waste(packaging, materials)
        
        if lang == 'fr':
            explanation = [
                f"Résultat de la classification: {classification[0]} (confiance: {classification[2]:.2%})",
                f"Description: {classification[1]}",
                "\nScores par poubelle:",
            ]
        else:
            explanation = [
                f"Classification result: {classification[0]} (confidence: {classification[2]:.2%})",
                f"Description: {classification[1]}",
                "\nBin scores:",
            ]
        
        for bin_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            explanation.append(f"- {bin_type}: {score:.2f}")
            
        return "\n".join(explanation)

# Example usage
def main():
    classifier = WasteClassifier()
    
    # Test cases in both languages
    test_cases = [
        # English cases
        ("glass bottle", ["glass"]),
        ("sandwich packaging", ["plastic", "aluminum"]),
        ("tin can", ["metal", "paper"]),
        ("milk bottle", ["plastic", "cardboard"]),
        # French cases
        ("bouteille en verre", ["verre"]),
        ("emballage sandwich", ["plastique", "aluminium"]),
        ("boîte de conserve", ["métal", "papier"]),
        ("bouteille de lait", ["plastique", "carton"]),
    ]
    
    for packaging, materials in test_cases:
        print("\nTest Case:")
        print(f"Packaging: {packaging}")
        print(f"Materials: {', '.join(materials)}")
        print("\nDetailed Analysis:")
        print(classifier.explain_classification(packaging, materials))


if __name__ == "__main__":
    main()