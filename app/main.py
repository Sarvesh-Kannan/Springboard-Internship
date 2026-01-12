from fastapi import FastAPI
from app.routers import lease

app = FastAPI(
    title="Car Lease LLM API",
    description="API for extracting structured data from car lease contracts",
    version="1.0.0"
)

app.include_router(lease.router)


@app.get("/")
def health_check():
    return {"status": "ok"}
