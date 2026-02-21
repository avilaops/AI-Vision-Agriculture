"""Test script for AI-Vision API with pytest."""

import pytest
from datetime import datetime
from io import BytesIO
from PIL import Image

from src.models import GPSCoordinates, VisionAnalysisRequest
from src.analyzer import VisionAnalyzer


def create_test_image(width: int = 640, height: int = 480, color: tuple = (34, 139, 34)) -> bytes:
    """Create a test image and return as bytes."""
    img = Image.new('RGB', (width, height), color=color)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    return buffer.getvalue()


@pytest.fixture
def analyzer():
    """Create a VisionAnalyzer instance."""
    return VisionAnalyzer(model_version="test-v0.1")


@pytest.fixture
def test_gps():
    """Create test GPS coordinates."""
    return GPSCoordinates(lat=-21.1234, lon=-47.5678, altitude=580.0)


def test_analyzer_initialization(analyzer):
    """Test that analyzer initializes correctly."""
    assert analyzer.model_version == "test-v0.1"
    assert analyzer._initialized is True


def test_model_info(analyzer):
    """Test model info retrieval."""
    info = analyzer.get_model_info()
    assert info["model_version"] == "test-v0.1"
    assert info["model_type"] == "placeholder"
    assert "maturity_analysis" in info["capabilities"]
    assert info["status"] == "initialized"


def test_analyze_image_bytes(analyzer, test_gps):
    """Test analyzing image from bytes."""
    image_bytes = create_test_image()
    
    result = analyzer.analyze_image_bytes(
        image_bytes=image_bytes,
        image_id="test_img_001.jpg",
        gps=test_gps,
        timestamp=datetime(2026, 2, 20, 10, 30, 0),
    )
    
    # Verify response structure
    assert result.image_id == "test_img_001.jpg"
    assert result.gps.lat == -21.1234
    assert result.gps.lon == -47.5678
    assert result.maturity.level in ["immature", "early_maturity", "ready_to_harvest", "late_harvest", "overripe"]
    assert 0.0 <= result.maturity.confidence <= 1.0
    assert 0.0 <= result.maturity.estimated_atr <= 25.0
    assert result.processing_time_ms > 0
    assert result.model_version == "test-v0.1"


def test_image_validation_format(analyzer, test_gps):
    """Test that invalid image formats are rejected."""
    # Create a BMP image (not supported)
    img = Image.new('RGB', (640, 480), color=(34, 139, 34))
    buffer = BytesIO()
    img.save(buffer, format='BMP')
    
    with pytest.raises(ValueError, match="Unsupported image format"):
        analyzer.analyze_image_bytes(
            image_bytes=buffer.getvalue(),
            image_id="test.bmp",
            gps=test_gps,
            timestamp=datetime.utcnow(),
        )


def test_image_validation_size_too_small(analyzer, test_gps):
    """Test that images below minimum size are rejected."""
    image_bytes = create_test_image(width=100, height=100)
    
    with pytest.raises(ValueError, match="Image too small"):
        analyzer.analyze_image_bytes(
            image_bytes=image_bytes,
            image_id="test_small.jpg",
            gps=test_gps,
            timestamp=datetime.utcnow(),
        )


def test_image_validation_size_too_large(analyzer, test_gps):
    """Test that images above maximum size are rejected."""
    image_bytes = create_test_image(width=5000, height=5000)
    
    with pytest.raises(ValueError, match="Image too large"):
        analyzer.analyze_image_bytes(
            image_bytes=image_bytes,
            image_id="test_large.jpg",
            gps=test_gps,
            timestamp=datetime.utcnow(),
        )


def test_maturity_analysis_consistency(analyzer, test_gps):
    """Test that maturity analysis is consistent for same inputs."""
    image_bytes = create_test_image()
    
    result1 = analyzer.analyze_image_bytes(
        image_bytes=image_bytes,
        image_id="test_img_001.jpg",
        gps=test_gps,
        timestamp=datetime(2026, 2, 20, 10, 30, 0),
    )
    
    result2 = analyzer.analyze_image_bytes(
        image_bytes=image_bytes,
        image_id="test_img_001.jpg",
        gps=test_gps,
        timestamp=datetime(2026, 2, 20, 10, 30, 0),
    )
    
    # Should return same maturity level (due to seeded randomness)
    assert result1.maturity.level == result2.maturity.level
    assert result1.maturity.estimated_atr == result2.maturity.estimated_atr


def test_gps_validation():
    """Test GPS coordinate validation."""
    # Valid coordinates
    gps = GPSCoordinates(lat=-21.1234, lon=-47.5678)
    assert gps.lat == -21.1234
    assert gps.lon == -47.5678
    
    # Invalid latitude (out of Brazil range)
    with pytest.raises(ValueError, match="Latitude must be between"):
        GPSCoordinates(lat=0.0, lon=-47.5678)
    
    # Invalid longitude (out of Brazil range)
    with pytest.raises(ValueError, match="Longitude must be between"):
        GPSCoordinates(lat=-21.1234, lon=-20.0)


def test_response_json_serialization(analyzer, test_gps):
    """Test that response can be serialized to JSON."""
    image_bytes = create_test_image()
    
    result = analyzer.analyze_image_bytes(
        image_bytes=image_bytes,
        image_id="test_img_001.jpg",
        gps=test_gps,
        timestamp=datetime(2026, 2, 20, 10, 30, 0),
    )
    
    # Should be serializable to dict
    result_dict = result.model_dump()
    assert isinstance(result_dict, dict)
    assert "image_id" in result_dict
    assert "maturity" in result_dict
    assert "pests" in result_dict
    assert "diseases" in result_dict
