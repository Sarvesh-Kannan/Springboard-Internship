import requests

NHTSA_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"

def lookup_vin(vin: str) -> dict:
    response = requests.get(
        NHTSA_URL.format(vin=vin),
        timeout=10
    )
    response.raise_for_status()

    results = response.json().get("Results", [])

    decoded = {}
    for item in results:
        if item.get("Value"):
            decoded[item["Variable"]] = item["Value"]

    return {
        "manufacturer": decoded.get("Manufacturer Name"),
        "make": decoded.get("Make"),
        "model": decoded.get("Model"),
        "model_year": decoded.get("Model Year"),
        "vehicle_type": decoded.get("Vehicle Type"),
        "plant_country": decoded.get("Plant Country"),
        "body_class": decoded.get ("Body Class"),
        "raw": decoded
    }
