#!/usr/bin/env python3
"""Test si la clé API Anthropic est valide et a des crédits."""

import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic, APIConnectionError, APIError

load_dotenv()

def test_api_key():
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()

    if not api_key:
        print("[FAIL] ANTHROPIC_API_KEY not defined")
        return False

    print(f"[OK] API key found: {api_key[:20]}...{api_key[-10:]}")

    try:
        print("\n[TEST 1] Creating Anthropic client...")
        client = Anthropic(api_key=api_key)
        print("[OK] Client created")

        print("\n[TEST 2] Calling API...")
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'API works!' in one word"}]
        )
        print(f"[OK] API works! Response: {response.content[0].text}")
        return True

    except APIConnectionError as e:
        print(f"\n[FAIL] CONNECTION ERROR: {str(e)}")
        print(f"Type: {type(e).__name__}")
        return False
    except APIError as e:
        print(f"\n[FAIL] API ERROR: {str(e)}")
        print(f"Type: {type(e).__name__}")
        if "unauthorized" in str(e).lower() or "invalid" in str(e).lower():
            print("   -> Invalid or expired API key")
        elif "quota" in str(e).lower() or "credit" in str(e).lower():
            print("   -> Insufficient credits")
        return False
    except Exception as e:
        print(f"\n[FAIL] ERROR: {str(e)}")
        print(f"Type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)
