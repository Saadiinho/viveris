from collections import defaultdict
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Tuple, Dict

class WasteClassifier:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-multilingual-cased')
        self.model = AutoModel.from_pretrained('distilbert-base-multilingual-cased')
        self.material_embeddings = {}

        # Expanded synonym dictionary with better multilingual coverage
        self.synonym_dict = {
            # Metal
            "aluminium": "metal", "aluminum": "metal", "metal": "metal",
            "canette": "metal", "can": "metal", "tin": "metal", "steel": "metal",
            "ferro": "metal", "boîte": "metal", "couvercle": "metal",
            "opercule": "metal", "conserva": "metal", "lata": "metal",
            
            # Plastic
            "pet": "plastic", "pet-1": "plastic", "hdpe-2": "plastic",
            "pp-5": "plastic", "polypropylene": "plastic", "plastic": "plastic",
            "polystyrene": "plastic", "sachet": "plastic", "film": "plastic",
            "sac": "plastic", "bottle": "plastic", "bouteille": "plastic",
            "emballage": "plastic", "packaging": "plastic", "flacon": "plastic",
            
            # Glass
            "verre": "glass", "glass": "glass", "bocal": "glass",
            "jar": "glass", "pot": "glass", "flacon": "glass",
            
            # Paper
            "paper": "paper", "papier": "paper", "cardboard": "paper",
            "carton": "paper", "tetra-pak": "paper", "tetra": "paper",
            "tetra brik": "paper", "kraft": "paper", "boîte": "paper",
            "enveloppe": "paper", "journal": "paper",
            
            # Organic
            "compost": "organic", "biodéchets": "organic", "shells": "organic",
            "peel": "organic", "food": "organic", "biodegradable": "organic"
        }

        # Enhanced reference material descriptions
        self.reference_materials = {
            'metal': self._get_embedding(
                "metal aluminium steel iron canette boîte-de-conserve "
                "capsule opercule couvercle conserva lata metal-container"
            ),
            'plastic': self._get_embedding(
                "plastic bottle sachet film bag packaging pet hdpe polypropylene "
                "polystyrene container emballage flacon bouteille plastique"
            ),
            'glass': self._get_embedding(
                "glass verre bocal jar pot glass-container flacon vitre "
                "bouteille-en-verre glass-bottle"
            ),
            'paper': self._get_embedding(
                "paper cardboard carton tetra-pak envelope kraft journal "
                "paper-packaging box sleeve corrugated non-corrugated"
            ),
            'organic': self._get_embedding(
                "organic food compost vegetable fruit peel shells "
                "biodegradable garden-waste biodéchets"
            )
        }

        self.bin_mapping = {
            'metal': 'rouge',
            'plastic': 'jaune',
            'glass': 'verte',
            'paper': 'bleue',
            'organic': 'marron'
        }

        self.ignore_tokens = {"non", "spécifié", "specifié", "none", "unknown", "recycle"}

    def _exact_dict_lookup(self, text: str) -> str:
        lower_text = text.lower().strip()
        
        # Special handling for composite materials
        if "tetra" in lower_text:
            return "paper"
        if "bouteille" in lower_text and "verre" in lower_text:
            return "glass"
            
        return self.synonym_dict.get(lower_text, "")

    def _get_embedding(self, text: str) -> torch.Tensor:
        if text in self.material_embeddings:
            return self.material_embeddings[text]
            
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1)
        self.material_embeddings[text] = embedding
        return embedding

    def _similarity_score(self, text1: str, text2: str) -> float:
        emb1 = self._get_embedding(text1)
        emb2 = self._get_embedding(text2)
        return torch.nn.functional.cosine_similarity(emb1, emb2).item()

    def _classify_single_material(self, mat: str) -> str:
        clean_mat = mat.lower().replace('en:', '').replace('fr:', '').strip()
        clean_mat = ''.join([c for c in clean_mat if c.isalnum() or c in {'-', '_'}])

        # Handle compound terms
        if '-' in clean_mat:
            for part in clean_mat.split('-'):
                if override := self._exact_dict_lookup(part):
                    return override

        if override := self._exact_dict_lookup(clean_mat):
            return override

        if clean_mat in self.ignore_tokens or len(clean_mat) < 2:
            return ""

        sim_map = {
            ref_type: self._similarity_score(clean_mat, ref_type)
            for ref_type in self.reference_materials
        }
        return max(sim_map.items(), key=lambda x: x[1])[0]

    def calculate_scores(self,
                         packaging: str,
                         materials: List[str],
                         packaging_materials_main: str = "") -> Dict[str, float]:
        scores = defaultdict(float)
        
        # Early exit if no usable data
        if not packaging and not materials and not packaging_materials_main:
            return scores

        # 0) Check for exact matches first (high reliability)
        exact_matches = []
        
        # Process packaging materials main first if exists
        if packaging_materials_main:
            main_clean = packaging_materials_main.lower().replace('en:', '').replace('fr:', '').strip()
            if main_clean in self.synonym_dict:
                return {self.bin_mapping[self.synonym_dict[main_clean]]: 100.0}  # Max confidence

        # 1) Process packaging text with exact match check
        if packaging.strip().lower() not in self.ignore_tokens:
            tokens = []
            for seg in packaging.replace('-', ' ').split(','):
                tokens.extend([part.strip() for part in seg.split()])
                
            for tok in tokens:
                lower_tok = tok.lower()
                if lower_tok in self.synonym_dict:
                    exact_matches.append(lower_tok)
                elif standard_mat := self._classify_single_material(tok):
                    bin_color = self.bin_mapping[standard_mat]
                    multiplier = 1.5
                    if self._exact_dict_lookup(tok.lower()):
                        scores[bin_color] += 1.0 * multiplier
                    else:
                        s = self._similarity_score(tok.lower(), standard_mat)
                        scores[bin_color] += s * multiplier

        # 2) Process materials list with exact match check
        material_exact_matches = []
        for mat in materials:
            lower_mat = mat.lower()
            if lower_mat in self.synonym_dict:
                material_exact_matches.append(lower_mat)
            elif standard_mat := self._classify_single_material(mat):
                bin_color = self.bin_mapping[standard_mat]
                multiplier = 2.0
                if self._exact_dict_lookup(mat.lower()):
                    scores[bin_color] += 1.0 * multiplier
                else:
                    s = self._similarity_score(mat.lower(), standard_mat)
                    scores[bin_color] += s * multiplier

        # 3) Handle exact matches with maximum confidence
        if exact_matches or material_exact_matches:
            all_matches = exact_matches + material_exact_matches
            match_counts = defaultdict(int)
            for match in all_matches:
                category = self.synonym_dict[match]
                match_counts[category] += 1
            
            if match_counts:
                main_category = max(match_counts.items(), key=lambda x: x[1])[0]
                return {self.bin_mapping[main_category]: 100.0}

        # 4) Handle material combinations
        elif len(materials) > 1:
            detected = {self._classify_single_material(m) for m in materials}
            if 'plastic' in detected and 'metal' in detected:
                scores['jaune'] *= 2.0
            if 'paper' in detected and 'plastic' in detected:
                scores['bleue'] *= 1.5

        return dict(scores)

    def classify_waste(self,
                       packaging: str,
                       materials: List[str] = None,
                       packaging_materials_main: str = "") -> Tuple[str, float]:
        materials = materials or []
        
        # Immediate unknown if no data
        if not packaging and not materials and not packaging_materials_main:
            return ("unknown", 0.0)
        
        # Check for main material override
        if packaging_materials_main:
            main_clean = packaging_materials_main.lower().replace('en:', '').replace('fr:', '').strip()
            if main_clean in self.synonym_dict:
                return (self.bin_mapping[self.synonym_dict[main_clean]], 1.0)

        scores = self.calculate_scores(packaging, materials, packaging_materials_main)

        if not scores:
            return ("unknown", 0.0)

        best_bin, best_score = max(scores.items(), key=lambda x: x[1])
        
        # Confidence thresholds
        if best_score < 0.5:  # Adjust this threshold as needed
            return ("unknown", 0.0)
            
        confidence = min(best_score, 1.0)
        return (best_bin, confidence)


# Helper functions remain the same

##################################################################
# HELPER FUNCTIONS
##################################################################
def get_bin_score(bin_color: str) -> int:
    """
    Convert bin color to a numerical score based on recyclability.
    """
    scoring_system = {
        'verte': 4,    # Glass is highly recyclable
        'jaune': 2,    # Plastic/cardboard
        'bleue': 3,    # Paper
        'rouge': 6,    # Metal
        'noire': 3,    # General waste
        'marron': 6,   # Organic waste
        'special': 10, # Special/hazardous
    }
    return scoring_system.get(bin_color, 1)

def get_product_type(bin_color: str) -> str:
    if bin_color == "unknown":
        return "Unknown Product Type"
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
