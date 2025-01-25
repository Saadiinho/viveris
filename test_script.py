import requests
import json

# List of barcodes
barcodes = [
  "3017620425035",
  "3017620422003",
  "5449000000996",
  "50184453",
  "4311501688144",
  "3451080155161",
  "5055904223289",
  "3474341105842",
  "54491472",
  "7300400481588",
  "3068320123264",
  "3225350000501",
  "3608580065340",
  "3155251205296",
  "3041090063206",
  "20995553",
  "20022464",
  "3155250358788",
  "5449000000286",
  "7394376616228",
  "06175700",
  "3045140105502",
  "3587220002252",
  "3760020507350",
  "3229820019307",
  "3017620429484",
  "3041090063114",
  "5411188124689",
  "59032823",
  "3046920028004",
  "7613035676497",
  "5449000054227",
  "16256866",
  "3366321051983",
  "5449000131836",
  "7613035974685",
  "5010029000016",
  "3229820782560",
  "3088543506255",
  "3017760542890",
  "4056489007180",
  "7622210713889",
  "3061990143365",
  "3366321052386",
  "3256540000698",
  "3046920028363",
  "3229820100234",
  "7300400481571",
  "3175680011442",
  "3046920029780"
]


def test_barcodes_against_backend():
    # Replace with your actual POST endpoint
    url = "http://localhost:8000/api/scanner/scan/"

    # We'll collect results in a list of dicts
    results = []

    for code in barcodes:
        try:
            payload = {"barcode": code}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Extract fields (adjust keys to match your actual JSON)
            name = data.get("name", "No name")
            packaging = data.get("packaging", "No packaging")
            packaging_materials = data.get("packaging_materials", [])
            packaging_materials_main = data.get("packagings_materials_main", "")
            color = data.get("recycling_bin", "No bin color")
            
            # Store the relevant info in a dict
            result_item = {
                "barcode": code,
                "name": name,
                "packaging": packaging,
                "packaging_materials": packaging_materials,
                "packaging_materials_main": packaging_materials_main,
                "bin_color": color
            }
            results.append(result_item)

        except requests.exceptions.RequestException as e:
            # If there's an error, we can store partial info or skip
            print(f"ERROR requesting barcode {code}: {e}")
            # You could store an error record if needed:
            # results.append({"barcode": code, "error": str(e)})

    # Finally, save all results to a JSON file
    with open("barcodes_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Finished fetching and saved results to barcodes_results.json")


if __name__ == "__main__":
    test_barcodes_against_backend()
