from fastapi import APIRouter, UploadFile, File
import os
os.makedirs("uploads", exist_ok=True)


from extract_text import extract_text
from fineline import process_text

router = APIRouter(prefix="/lease", tags=["Lease Extraction"])

@router.post("/extract")
async def extract_lease(file: UploadFile = File(...)):
    temp_path = f"uploads/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text(temp_path)
    lease_data = process_text(raw_text)

    os.remove(temp_path)

    return {
        "filename": file.filename,
        "lease_details": lease_data
    }


