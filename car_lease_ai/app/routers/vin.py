from fastapi import APIRouter, HTTPException
from utils import is_valid_vin
from app.services.vin_lookup import lookup_vin

router = APIRouter(
    prefix="/vin",
    tags=["VIN Lookup"]
)

@router.get("/lookup/{vin}")
async def vin_lookup(vin: str):
    vin = vin.upper()

    # 1️⃣ Validate VIN format
    if not is_valid_vin(vin):
        raise HTTPException(
            status_code=400,
            detail="Invalid VIN format. VIN must be 17 characters."
        )

    try:
        # 2️⃣ Decode VIN
        vin_data = lookup_vin(vin)

        if not vin_data or not vin_data.get("make"):
            return {
                "vin": vin,
                "status": "not_found",
                "message": "VIN could not be decoded"
            }

        return {
            "vin": vin,
            "status": "verified",
            "vehicle_details": {
                "manufacturer": vin_data.get("manufacturer"),
                "make": vin_data.get("make"),
                "model": vin_data.get("model"),
                "model_year": vin_data.get("model_year"),
                "vehicle_type": vin_data.get("vehicle_type"),
                "plant_country": vin_data.get("plant_country")
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"VIN lookup failed: {str(e)}"
        )
