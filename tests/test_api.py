#!/usr/bin/env python3
"""
Quick test script to check Anthropic API access and available models.
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ No ANTHROPIC_API_KEY found in .env")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")
print()

# Try to create a client
try:
    client = anthropic.Anthropic(api_key=api_key)
    print("✓ Client created successfully")
    print()
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    exit(1)

# Try a simple message with different models
models_to_test = [
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-20241022",
]

print("Testing models:")
print("-" * 60)

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✓ {model} - WORKS")
    except anthropic.NotFoundError:
        print(f"✗ {model} - NOT FOUND (404)")
    except anthropic.AuthenticationError:
        print(f"✗ {model} - AUTH ERROR (invalid key)")
    except anthropic.PermissionDeniedError:
        print(f"✗ {model} - PERMISSION DENIED")
    except Exception as e:
        print(f"✗ {model} - ERROR: {type(e).__name__}")

print()
print("=" * 60)
print("If all models show 'NOT FOUND', your API key might be:")
print("  1. For a different API endpoint/region")
print("  2. Expired or invalid")
print("  3. A console.anthropic.com key (not API key)")
print()
print("Try getting a new API key from: https://console.anthropic.com/settings/keys")
