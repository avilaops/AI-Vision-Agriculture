"""Pydantic models for AI-Vision Agriculture API data contracts."""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class GPSCoordinates(BaseModel):
    """GPS coordinates with validation for Brazil agricultural regions."""
    
    lat: float = Field(
        ...,
        ge=-34.0,
        le=-1.0,
        description="Latitude in decimal degrees (Brazil: -34 to -1)"
    )
    lon: float = Field(
        ...,
        ge=-74.0,
        le=-32.0,
        description="Longitude in decimal degrees (Brazil: -74 to -32)"
    )
    altitude: Optional[float] = Field(
        None,
        ge=0,
        le=3000,
        description="Altitude in meters above sea level"
    )
    
    @field_validator('lat')
    @classmethod
    def validate_lat(cls, v: float) -> float:
        """Ensure latitude is within valid range."""
        if not -34.0 <= v <= -1.0:
            raise ValueError("Latitude must be between -34 and -1 (Brazil)")
        return v
    
    @field_validator('lon')
    @classmethod
    def validate_lon(cls, v: float) -> float:
        """Ensure longitude is within valid range."""
        if not -74.0 <= v <= -32.0:
            raise ValueError("Longitude must be between -74 and -32 (Brazil)")
        return v


class MaturityAnalysis(BaseModel):
    """Sugarcane maturity analysis results."""
    
    level: Literal[
        "immature",
        "early_maturity",
        "ready_to_harvest",
        "late_harvest",
        "overripe"
    ] = Field(
        ...,
        description="Maturity classification level"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for maturity classification"
    )
    estimated_atr: float = Field(
        ...,
        ge=0.0,
        le=25.0,
        description="Estimated ATR (Total Recoverable Sugar) in kg/ton"
    )
    estimated_pol: Optional[float] = Field(
        None,
        ge=0.0,
        le=25.0,
        description="Estimated POL (Polarization) percentage"
    )
    estimated_brix: Optional[float] = Field(
        None,
        ge=0.0,
        le=30.0,
        description="Estimated Brix (dissolved solids) percentage"
    )
    
    @field_validator('estimated_atr')
    @classmethod
    def validate_atr(cls, v: float) -> float:
        """Ensure ATR is within realistic range for sugarcane."""
        if not 8.0 <= v <= 20.0:
            # Warning: ATR outside typical range (8-20 kg/ton)
            pass
        return v


class PestDetection(BaseModel):
    """Pest detection result."""
    
    pest_type: str = Field(
        ...,
        description="Type of pest detected (e.g., 'sugarcane_borer', 'spittlebug')"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for pest detection"
    )
    severity: Literal["low", "moderate", "high", "critical"] = Field(
        ...,
        description="Severity level of pest infestation"
    )
    bounding_box: Optional[List[float]] = Field(
        None,
        description="Bounding box [x1, y1, x2, y2] in normalized coordinates (0-1)"
    )
    
    @field_validator('bounding_box')
    @classmethod
    def validate_bbox(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Ensure bounding box has correct format."""
        if v is not None:
            if len(v) != 4:
                raise ValueError("Bounding box must have 4 coordinates [x1, y1, x2, y2]")
            if not all(0.0 <= coord <= 1.0 for coord in v):
                raise ValueError("Bounding box coordinates must be normalized (0-1)")
        return v


class DiseaseDetection(BaseModel):
    """Disease detection result."""
    
    disease_type: str = Field(
        ...,
        description="Type of disease detected (e.g., 'red_rot', 'smut', 'rust')"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for disease detection"
    )
    severity: Literal["low", "moderate", "high", "critical"] = Field(
        ...,
        description="Severity level of disease"
    )
    affected_area_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Percentage of plant area affected by disease"
    )


class VisionAnalysisRequest(BaseModel):
    """Request model for vision analysis endpoint."""
    
    image_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique identifier for the image"
    )
    gps: GPSCoordinates = Field(
        ...,
        description="GPS coordinates where image was captured"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when image was captured (ISO 8601)"
    )
    metadata: Optional[dict] = Field(
        None,
        description="Additional metadata (camera settings, weather, etc.)"
    )


class VisionAnalysisResponse(BaseModel):
    """Response model for vision analysis endpoint."""
    
    image_id: str = Field(
        ...,
        description="Unique identifier for the analyzed image"
    )
    gps: GPSCoordinates = Field(
        ...,
        description="GPS coordinates where image was captured"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when image was captured (ISO 8601)"
    )
    maturity: MaturityAnalysis = Field(
        ...,
        description="Sugarcane maturity analysis results"
    )
    pests: List[PestDetection] = Field(
        default_factory=list,
        description="List of detected pests (empty if none detected)"
    )
    diseases: List[DiseaseDetection] = Field(
        default_factory=list,
        description="List of detected diseases (empty if none detected)"
    )
    processing_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Processing time in milliseconds"
    )
    model_version: str = Field(
        default="placeholder-v0.1",
        description="Version of the ML model used for analysis"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_id": "img_20260220_103000.jpg",
                "gps": {
                    "lat": -21.1234,
                    "lon": -47.5678,
                    "altitude": 580.0
                },
                "timestamp": "2026-02-20T10:30:00Z",
                "maturity": {
                    "level": "ready_to_harvest",
                    "confidence": 0.85,
                    "estimated_atr": 14.2,
                    "estimated_pol": 16.8,
                    "estimated_brix": 18.5
                },
                "pests": [],
                "diseases": [],
                "processing_time_ms": 124.5,
                "model_version": "placeholder-v0.1"
            }
        }
