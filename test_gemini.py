#!/usr/bin/env python3
"""
Quick test script to check Gemini API access.
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ No GOOGLE_API_KEY found in .env")
    print("Get one from: https://makersuite.google.com/app/apikey")
    exit(1)

print(f"✓ Google API Key found: {api_key[:20]}...")
print()

try:
    import google.generativeai as genai
    print("✓ google-generativeai package installed")
except ImportError:
    print("❌ google-generativeai not installed")
    print("Run: pip install google-generativeai")
    exit(1)

print()

# Configure
genai.configure(api_key=api_key)

# Try to list models
print("Available Gemini models:")
print("-" * 60)

try:
    models = genai.list_models()
    found_any = False
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            found_any = True

    if not found_any:
        print("❌ No models found that support content generation")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    exit(1)

print()
print("-" * 60)

# Test a simple generation
print("\nTesting simple generation...")
models_to_test = [
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-pro",
]

for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'test'")
        print(f"✓ {model_name} - WORKS")
        print(f"  Response: {response.text[:50]}...")
        break
    except Exception as e:
        print(f"✗ {model_name} - ERROR: {type(e).__name__}: {str(e)[:60]}")

print()
print("=" * 60)
print("If you see models listed above, Gemini is working!")
print("Run with: python benchmark.py --model gemini --limit 2")
