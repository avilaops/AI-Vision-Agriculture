"""Quick validation script for AI-Vision API"""
from src.api import app
from src.analyzer import VisionAnalyzer

print("✓ API import successful")
analyzer = VisionAnalyzer()
print("✓ Analyzer initialized")
info = analyzer.get_model_info()
print(f"✓ Model: {info['model_version']}, Status: {info['status']}")
print("✓ All imports and initialization working!")
