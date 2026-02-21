"""FastAPI application for AI-Vision Agriculture analysis."""

from datetime import datetime
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from .analyzer import VisionAnalyzer
from .models import GPSCoordinates, VisionAnalysisResponse


# Initialize FastAPI app
app = FastAPI(
    title="AI-Vision Agriculture API",
    description="Computer vision API for sugarcane maturity analysis, pest and disease detection",
    version="0.1.0",
    contact={
        "name": "AvilaOps",
        "url": "https://github.com/avilaops/AI-Vision-Agriculture",
    },
    license_info={
        "name": "MIT",
    },
)

# Initialize analyzer
analyzer = VisionAnalyzer(model_version="placeholder-v0.1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "AI-Vision Agriculture API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "analyze": "/analyze (POST)",
            "health": "/health (GET)",
            "model_info": "/model-info (GET)",
            "docs": "/docs (GET)",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "analyzer": analyzer.get_model_info(),
    }


@app.get("/model-info")
async def model_info():
    """Get information about the loaded ML model."""
    return analyzer.get_model_info()


@app.post(
    "/analyze",
    response_model=VisionAnalysisResponse,
    summary="Analyze sugarcane field image",
    description="Upload a sugarcane field image with GPS metadata for maturity analysis, pest and disease detection",
)
async def analyze_image(
    image: UploadFile = File(
        ...,
        description="Image file (JPEG or PNG, min 224x224, max 4096x4096)"
    ),
    image_id: str = Form(
        ...,
        description="Unique identifier for the image"
    ),
    lat: float = Form(
        ...,
        ge=-34.0,
        le=-1.0,
        description="Latitude in decimal degrees (Brazil: -34 to -1)"
    ),
    lon: float = Form(
        ...,
        ge=-74.0,
        le=-32.0,
        description="Longitude in decimal degrees (Brazil: -74 to -32)"
    ),
    altitude: Optional[float] = Form(
        None,
        ge=0,
        le=3000,
        description="Altitude in meters above sea level"
    ),
    timestamp: Optional[str] = Form(
        None,
        description="Timestamp when image was captured (ISO 8601 format). Defaults to current time."
    ),
) -> VisionAnalysisResponse:
    """
    Analyze a sugarcane field image.
    
    This endpoint accepts:
    - An image file (JPEG or PNG)
    - GPS coordinates (latitude, longitude, optional altitude)
    - Image metadata (ID, timestamp)
    
    Returns:
    - Maturity analysis (level, confidence, estimated ATR/POL/Brix)
    - Pest detections (if any)
    - Disease detections (if any)
    - Processing time and model version
    """
    try:
        # Validate image content type
        if image.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format: {image.content_type}. Use JPEG or PNG."
            )
        
        # Read image bytes
        image_bytes = await image.read()
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty image file")
        
        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=413,
                detail="Image file too large. Maximum 10MB."
            )
        
        # Parse timestamp
        if timestamp:
            try:
                parsed_timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid timestamp format: {e}. Use ISO 8601 format."
                )
        else:
            parsed_timestamp = datetime.utcnow()
        
        # Create GPS coordinates
        gps = GPSCoordinates(
            lat=lat,
            lon=lon,
            altitude=altitude,
        )
        
        # Analyze image
        result = analyzer.analyze_image_bytes(
            image_bytes=image_bytes,
            image_id=image_id,
            gps=gps,
            timestamp=parsed_timestamp,
        )
        
        return result
        
    except ValueError as e:
        # Validation errors from Pydantic or PIL
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during image analysis: {str(e)}"
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for better error messages."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
