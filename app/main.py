"""FastAPI application"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
from app.core.router import xray_router
from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

app = FastAPI(
    title="Radiology AI API",
    description="AI-powered X-ray report generation for Nigerian diagnostic centers",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Radiology AI API",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/analyze-xray")
async def analyze_xray(
    file: UploadFile = File(...),
    image_type: str = "chest",
    patient_age: int = None,
    clinical_indications: str = None,
):
    """
    Analyze X-ray image and generate report
    
    Args:
        file: X-ray image (JPEG/PNG)
        image_type: "chest" or "limb"
    
    Returns:
        Triage info + draft report
    """
    try:
        # Validate file type
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(400, "Only JPEG/PNG images allowed")
        
        # Read and encode image
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode()
        
        logger.info(f"Analyzing {image_type} X-ray: {file.filename}")
        
        # Process through pipeline
        result = await xray_router.analyze_xray(
            image_base64=image_base64,
            image_type=image_type,
            patient_age=patient_age,
            clinical_indications=clinical_indications
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )