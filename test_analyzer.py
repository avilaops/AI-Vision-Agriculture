"""Quick test of analyzer with mock image"""
from PIL import Image
from io import BytesIO
from datetime import datetime
from src.analyzer import VisionAnalyzer
from src.models import GPSCoordinates

# Create analyzer
analyzer = VisionAnalyzer()

# Create test image
img = Image.new('RGB', (640, 480), color=(34, 139, 34))
buffer = BytesIO()
img.save(buffer, format='JPEG')
image_bytes = buffer.getvalue()

# Test analysis
gps = GPSCoordinates(lat=-21.1234, lon=-47.5678, altitude=580.0)
result = analyzer.analyze_image_bytes(
    image_bytes=image_bytes,
    image_id="test_001.jpg",
    gps=gps,
    timestamp=datetime(2026, 2, 20, 10, 30, 0)
)

# Print results
print(f"✓ Analysis completed")
print(f"  Image ID: {result.image_id}")
print(f"  GPS: ({result.gps.lat}, {result.gps.lon})")
print(f"  Maturity: {result.maturity.level}")
print(f"  Confidence: {result.maturity.confidence:.1%}")
print(f"  Estimated ATR: {result.maturity.estimated_atr:.1f} kg/ton")
print(f"  Pests detected: {len(result.pests)}")
print(f"  Diseases detected: {len(result.diseases)}")
print(f"  Processing time: {result.processing_time_ms:.1f}ms")
print(f"✓ Mock analysis working correctly!")
