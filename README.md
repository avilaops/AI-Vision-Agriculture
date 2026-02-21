# AI-Vision-Agriculture

Computer vision API for sugarcane maturity analysis, pest detection, and disease detection. Part of the AvilaOps agricultural technology ecosystem.

## 🎯 Overview

This service provides a REST API for analyzing sugarcane field images, returning:
- **Maturity analysis**: Classification level, confidence score, estimated ATR/POL/Brix
- **Pest detection**: Identification of common sugarcane pests with bounding boxes
- **Disease detection**: Detection of diseases with severity assessment

**Current Status**: Placeholder implementation with mock results. ML model training will be added in Phase 2.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/avilaops/AI-Vision-Agriculture.git
cd AI-Vision-Agriculture

# Install dependencies
pip install -r requirements.txt
```

### Running the API Server

```bash
# Start the FastAPI server
uvicorn src.api:app --reload

# Server will start at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### Testing the API

```bash
# Run the example script
python examples/analyze_image.py

# Or use curl
curl -X POST "http://localhost:8000/analyze" \
  -F "image=@test_image.jpg" \
  -F "image_id=img_001.jpg" \
  -F "lat=-21.1234" \
  -F "lon=-47.5678" \
  -F "altitude=580.0"
```

## 📡 API Endpoints

### `POST /analyze`

Analyze a sugarcane field image.

**Request:**
- `image`: Image file (JPEG or PNG, 224x224 to 4096x4096 pixels, max 10MB)
- `image_id`: Unique identifier for the image
- `lat`: Latitude in decimal degrees (Brazil: -34 to -1)
- `lon`: Longitude in decimal degrees (Brazil: -74 to -32)
- `altitude`: Altitude in meters (optional)
- `timestamp`: ISO 8601 timestamp (optional, defaults to current time)

**Response:**

```json
{
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
```

### `GET /health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-02-20T10:30:00Z",
  "analyzer": {
    "model_version": "placeholder-v0.1",
    "model_type": "placeholder",
    "capabilities": ["maturity_analysis", "pest_detection", "disease_detection"],
    "status": "initialized"
  }
}
```

### `GET /model-info`

Get information about the loaded ML model.

### `GET /docs`

Interactive API documentation (Swagger UI).

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Project Structure

```
AI-Vision-Agriculture/
├── src/
│   ├── __init__.py          # Package exports
│   ├── api.py               # FastAPI application
│   ├── models.py            # Pydantic data models
│   └── analyzer.py          # Image analysis logic (placeholder)
├── tests/
│   └── test_analyzer.py     # Unit tests
├── examples/
│   └── analyze_image.py     # Example usage script
├── docs/
│   └── (OpenAPI spec auto-generated at /docs)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 📊 Data Contract

### Maturity Levels

- `immature`: Not ready for harvest (ATR < 12 kg/ton)
- `early_maturity`: Early maturity (ATR 12-13 kg/ton)
- `ready_to_harvest`: Optimal harvest time (ATR 13-16 kg/ton)
- `late_harvest`: Late harvest window (ATR 13-15 kg/ton)
- `overripe`: Past optimal harvest (ATR declining)

### Pest Types (Examples)

- `sugarcane_borer`: Diatraea saccharalis
- `spittlebug`: Mahanarva fimbriolata
- `white_grub`: Migdolus fryanus
- `aphid`: Melanaphis sacchari

### Disease Types (Examples)

- `red_rot`: Colletotrichum falcatum
- `smut`: Sporisorium scitamineum
- `rust`: Puccinia melanocephala
- `mosaic_virus`: Sugarcane Mosaic Virus (SCMV)

## 🔗 Integration

This service integrates with:

- **CanaSwarm-Intelligence**: Provides real-time field analysis for fleet coordination
- **Precision-Agriculture-Platform**: Enriches harvest data with maturity predictions
- **AgriBot-Retrofit**: Processes images from autonomous robot cameras

### Example Integration (Python)

```python
import requests
from datetime import datetime

def analyze_field_image(image_path: str, lat: float, lon: float):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/analyze',
            data={
                'image_id': 'field_001.jpg',
                'lat': lat,
                'lon': lon,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
            },
            files={'image': f}
        )
    return response.json()

# Usage
results = analyze_field_image('sugarcane_field.jpg', -21.1234, -47.5678)
print(f"Maturity: {results['maturity']['level']}")
print(f"Estimated ATR: {results['maturity']['estimated_atr']} kg/ton")
```

## 🚧 Roadmap

### Phase 1 (Current) - Infrastructure
- [x] API skeleton with FastAPI
- [x] Data contract definition (Pydantic models)
- [x] Placeholder analyzer with mock results
- [x] OpenAPI documentation
- [x] Integration examples

### Phase 2 - ML Model Development (Q2 2026)
- [ ] Dataset collection and labeling
- [ ] Model training (CNN for maturity, YOLO for pests/diseases)
- [ ] Model evaluation and calibration
- [ ] Model deployment

### Phase 3 - Production (Q3 2026)
- [ ] Model versioning and A/B testing
- [ ] Performance optimization
- [ ] Batch processing support
- [ ] Cloud deployment (AWS/Azure)

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Part of the AvilaOps agro-tech ecosystem. For contribution guidelines, see the main repository.

## 📧 Contact

- **Organization**: AvilaOps
- **Repository**: https://github.com/avilaops/AI-Vision-Agriculture
- **Issue Tracking**: GitHub Issues

---

**Note**: This is a placeholder implementation. The current version returns mock results for testing integration. ML model training will be added in Phase 2. 
