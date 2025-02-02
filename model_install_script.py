import os
import requests
from tqdm import tqdm  # Affiche une barre de progression

# 📌 Configuration
MODEL_DIR = "model"
MODEL_FILENAME = "fine_tuned_resnet50.keras"

# 📌 Chemin complet du fichier
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

# 📌 URL de téléchargement Google Drive
DOWNLOAD_URL = f"https://drive.google.com/file/d/1PqZasU83sIDwA3fLFuZk2mwx-BvtvgxH/view?usp=share_link"

# ✅ Vérifier si le modèle est déjà téléchargé
if os.path.exists(MODEL_PATH):
    print(f"✅ Le modèle existe déjà dans {MODEL_PATH}, pas besoin de le télécharger.")
else:
    print(f"📥 Téléchargement du modèle depuis Google Drive...")

    # Créer le dossier model/ s'il n'existe pas
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Télécharger avec une barre de progression
    response = requests.get(DOWNLOAD_URL, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(MODEL_PATH, "wb") as file, tqdm(
        desc="Téléchargement", total=total_size, unit="B", unit_scale=True
    ) as progress:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress.update(len(chunk))

    print(f"✅ Modèle téléchargé et enregistré dans {MODEL_PATH}")
