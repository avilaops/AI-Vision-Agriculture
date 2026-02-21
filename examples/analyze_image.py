"""Example script demonstrating AI-Vision API usage."""

import requests
from datetime import datetime
from pathlib import Path


def analyze_image_file(
    image_path: str,
    lat: float,
    lon: float,
    altitude: float = None,
    api_url: str = "http://localhost:8000"
) -> dict:
    """
    Analyze a sugarcane field image using the AI-Vision API.
    
    Args:
        image_path: Path to image file (JPEG or PNG)
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
        altitude: Altitude in meters (optional)
        api_url: Base URL of the API server
        
    Returns:
        Dictionary with analysis results
    """
    # Prepare the image file
    image_file = Path(image_path)
    if not image_file.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Prepare form data
    data = {
        "image_id": image_file.name,
        "lat": lat,
        "lon": lon,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    if altitude is not None:
        data["altitude"] = altitude
    
    # Prepare files
    with open(image_path, "rb") as f:
        files = {"image": (image_file.name, f, "image/jpeg")}
        
        # Send POST request
        response = requests.post(
            f"{api_url}/analyze",
            data=data,
            files=files,
            timeout=30,
        )
    
    # Check response
    response.raise_for_status()
    return response.json()


def print_analysis_results(results: dict) -> None:
    """Pretty print analysis results."""
    print("\n" + "="*60)
    print("AI-VISION ANALYSIS RESULTS")
    print("="*60)
    
    print(f"\n📍 Image: {results['image_id']}")
    print(f"📍 GPS: ({results['gps']['lat']:.6f}, {results['gps']['lon']:.6f})")
    if results['gps'].get('altitude'):
        print(f"📍 Altitude: {results['gps']['altitude']:.1f}m")
    print(f"📍 Timestamp: {results['timestamp']}")
    
    print(f"\n🌱 MATURITY ANALYSIS")
    maturity = results['maturity']
    print(f"   Level: {maturity['level'].replace('_', ' ').title()}")
    print(f"   Confidence: {maturity['confidence']:.1%}")
    print(f"   Estimated ATR: {maturity['estimated_atr']:.1f} kg/ton")
    if maturity.get('estimated_pol'):
        print(f"   Estimated POL: {maturity['estimated_pol']:.1f}%")
    if maturity.get('estimated_brix'):
        print(f"   Estimated Brix: {maturity['estimated_brix']:.1f}%")
    
    if results['pests']:
        print(f"\n🐛 PEST DETECTIONS ({len(results['pests'])})")
        for pest in results['pests']:
            print(f"   - {pest['pest_type']}: {pest['severity']} severity ({pest['confidence']:.1%} confidence)")
    else:
        print(f"\n🐛 PEST DETECTIONS: None")
    
    if results['diseases']:
        print(f"\n🦠 DISEASE DETECTIONS ({len(results['diseases'])})")
        for disease in results['diseases']:
            print(f"   - {disease['disease_type']}: {disease['severity']} severity ({disease['confidence']:.1%} confidence)")
            if disease.get('affected_area_pct'):
                print(f"     Affected area: {disease['affected_area_pct']:.1f}%")
    else:
        print(f"\n🦠 DISEASE DETECTIONS: None")
    
    print(f"\n⏱️  Processing time: {results['processing_time_ms']:.1f}ms")
    print(f"🤖 Model version: {results['model_version']}")
    print("="*60 + "\n")


def main():
    """Example usage of the AI-Vision API."""
    
    # Example 1: Analyze with a mock image
    print("Example 1: Creating a test image and analyzing...")
    
    # Create a simple test image (green square to simulate sugarcane)
    from PIL import Image
    test_image_path = "test_sugarcane.jpg"
    img = Image.new('RGB', (640, 480), color=(34, 139, 34))  # Forest green
    img.save(test_image_path, 'JPEG')
    
    try:
        # Analyze the test image
        # GPS coordinates for São Paulo sugarcane region
        results = analyze_image_file(
            image_path=test_image_path,
            lat=-21.1234,
            lon=-47.5678,
            altitude=580.0,
            api_url="http://localhost:8000"
        )
        
        # Print results
        print_analysis_results(results)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("   Make sure the server is running:")
        print("   python -m uvicorn src.api:app --reload")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up test image
        import os
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"✓ Cleaned up test image: {test_image_path}")


if __name__ == "__main__":
    main()
