from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid

from extract_text import extract_text
from fineline import process_text
from fairness_score import compute_fairness_score
from red_flags import detect_red_flags


router = APIRouter(
    prefix="/lease",
    tags=["Lease Extraction"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
async def lease_health():
    return {
        "service": "lease_extraction",
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


@router.post("/extract")
async def extract_lease(file: UploadFile = File(...)):
    # 1️⃣ Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # 2️⃣ Save uploaded file with unique name
    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)

    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # 3️⃣ Extract raw text from PDF
        raw_text = extract_text(temp_path)

        if not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from the PDF"
            )

        # 4️⃣ Run LLM extraction (THIS USES GEMINI)
        lease_data = process_text(raw_text)
        fairness = compute_fairness_score(lease_data)
        red_flags = detect_red_flags(lease_data)

        return {
            "success": True,
            "filename": file.filename,
            "lease_details": lease_data,
            "fairness_analysis": fairness,
            "red_flags": red_flags
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to process contract with LLM",
                "error_type": type(e).__name__,
                "details": str(e)
            }
        )

    finally:
        # 5️⃣ Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # 4️⃣ Run LLM extraction (THIS USES GEMINI)
        lease_data = process_text(raw_text)
        fairness = compute_fairness_score(lease_data)
        red_flags = detect_red_flags(lease_data)

        # 🔹 Inject Fairness Analysis into lease_details (UI-friendly)
        if fairness:
            lease_data["8. Fairness Analysis"] = {
                "Fairness Score": f"{fairness.get('fairness_score')} / 100",
                "Risk Category": fairness.get("category"),
                "Cost Transparency": f"{fairness['breakdown'].get('cost_transparency')} / 100",
                "Mileage Fairness": f"{fairness['breakdown'].get('mileage_fairness')} / 100",
                "Termination Clarity": f"{fairness['breakdown'].get('termination_clarity')} / 100",
                "Residual Logic": f"{fairness['breakdown'].get('residual_logic')} / 100",
                "Legal Clarity": f"{fairness['breakdown'].get('legal_clarity')} / 100"
            }

        # 🔹 Inject Red Flags into lease_details (UI-friendly)
        if red_flags:
            lease_data["9. Red Flags"] = {
                f"Flag {i+1}": flag for i, flag in enumerate(red_flags)
            }

        return {
            "success": True,
            "filename": file.filename,
            "lease_details": lease_data,
            "fairness_analysis": fairness,
            "red_flags": red_flags
        }
