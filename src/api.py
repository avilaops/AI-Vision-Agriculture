"""FastAPI application for AI-Vision Agriculture analysis."""

from datetime import datetime
from typing import Optional
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Query
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


# ========================================
# MOCK ENDPOINT FOR INTEGRATION TESTING
# ========================================

# Mock scenarios for testing Integration with Intelligence
MOCK_SCENARIOS = {
    "healthy": {
        "crop_health": {
            "status": "healthy",
            "confidence": 0.92,
            "ndvi": 0.82,
            "description": "Crop shows healthy growth with good vigor"
        },
        "weeds": [],
        "pests": [],
        "diseases": []
    },
    "weeds": {
        "crop_health": {
            "status": "stressed",
            "confidence": 0.87,
            "ndvi": 0.55,
            "description": "Crop under stress due to weed competition"
        },
        "weeds": [
            {
                "class": "braquiaria",
                "common_name": "Brachiaria / Capim-braquiária",
                "confidence": 0.92,
                "severity": "high",
                "area_m2": 125.5,
                "coverage_percent": 18.5,
                "description": "Widespread braquiaria infestation competing with crop"
            }
        ],
        "pests": [],
        "diseases": []
    },
    "pests": {
        "crop_health": {
            "status": "diseased",
            "confidence": 0.89,
            "ndvi": 0.48,
            "description": "Crop showing disease symptoms from pest damage"
        },
        "weeds": [],
        "pests": [
            {
                "class": "spodoptera_frugiperda",
                "common_name": "Lagarta-do-cartucho / Fall armyworm",
                "confidence": 0.91,
                "severity": "critical",
                "infestation_level": "high",
                "estimated_damage_percent": 25
            }
        ],
        "diseases": [
            {
                "class": "ferrugem_sugarcane",
                "common_name": "Ferrugem / Sugarcane rust",
                "confidence": 0.85,
                "severity": "medium",
                "affected_area_m2": 45.0,
                "symptoms": ["orange_pustules", "leaf_yellowing"]
            }
        ]
    }
}


@app.post("/api/v1/vision/analyze")
async def analyze_mock(
    file: Optional[UploadFile] = File(None),
    field_id: str = Query("F001", description="Field identifier"),
    zone_id: str = Query("Z001", description="Zone identifier"),
    scenario: str = Query("healthy", description="Mock scenario: healthy, weeds, pests")
):
    """
    Mock vision analysis endpoint for integration testing.
    
    Use 'scenario' parameter to control output:
    - healthy: Optimal crop health, no issues
    - weeds: High weed infestation
    - pests: Heavy pest infestation + disease
    """
    scenario_data = MOCK_SCENARIOS.get(scenario, MOCK_SCENARIOS["healthy"])
    
    analysis_id = f"VIS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    
    # Construct recommendations based on detections
    recommendations = []
    if scenario_data.get("weeds"):
        recommendations.append({
            "action": "apply_herbicide",
            "priority": "high",
            "reason": "High-severity weed infestation detected"
        })
    if scenario_data.get("pests"):
        recommendations.append({
            "action": "apply_pesticide",
            "priority": "critical",
            "reason": "Heavy pest infestation requires immediate control"
        })
    if scenario_data.get("diseases"):
        recommendations.append({
            "action": "apply_fungicide",
            "priority": "high",
            "reason": "Disease detected, prevent spread"
        })
    
    if not recommendations:
        recommendations.append({
            "action": "continue_monitoring",
            "priority": "low",
            "reason": "Crop health is optimal"
        })
    
    response = {
        "analysis_id": analysis_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {
            "device_id": "DRONE-V123",
            "device_type": "drone"
        },
        "location": {
            "field_id": field_id,
            "zone_id": zone_id
        },
        "detections": scenario_data,
        "recommendations": recommendations
    }
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
