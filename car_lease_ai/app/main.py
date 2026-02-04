"""
Car Lease LLM API - Main Application
FastAPI server for extracting structured data from car lease contracts
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import logging

# Create FastAPI app
app = FastAPI(
    title="Car Lease LLM API",
    description="""
    AI-powered API for extracting and analyzing car lease contracts.
    """,
    version="1.0.0",
    contact={
        "name": "Car Lease AI Team",
        "email": "ksarvesh200514@gmail.com"
    },
    license_info={
        "name": "MIT",
    }
)


# Import your routers
from app.routers import auth, lease, vin, chat_bot

# Include routers AFTER app is defined
app.include_router(auth.router)
app.include_router(lease.router)
app.include_router(vin.router)
app.include_router(chat_bot.router)


# Add CORS middleware (adjust origins as needed for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# UI
templates = Jinja2Templates(directory="app/templates")
app.mount("/Static", StaticFiles(directory="static"), name="static")


@app.get("/ui")
def ui(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/vinlookup")
def vinlookup(request: Request):
    return templates.TemplateResponse(
        "vinlookup.html",
        {"request": request}
    )

@app.get("/signup")
def signup_ui(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request}
    )


# ========================
# Configure logging
# ========================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================
# EXCEPTION HANDLERS
# ========================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    logger.error(f"Validation error: {exc}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "error_type": "RequestValidationError",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_type": type(exc).__name__,
            "details": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ========================
# ROOT  AND HEALTHENDPOINTS
# ========================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Car Lease LLM API",
        "version": "1.0.0",
        "status": "operational",
        "description": "API for extracting structured data from car lease contracts",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "lease_extraction": "/lease/extract",
            "lease_health": "/lease/health"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Global health check"""
    return {
        "status": "healthy",
        "service": "car-lease-llm-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ========================
# STARTUP / SHUTDOWN EVENTS
# ========================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Car Lease LLM API starting up...")
    logger.info("API Documentation available at: /docs")
    logger.info("API is ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Car Lease LLM API shutting down...")


