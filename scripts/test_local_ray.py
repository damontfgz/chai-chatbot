#!/usr/bin/env python3
"""
Local test script for Ray Serve application
Run this to test the chat completion service locally
"""

import os
import sys
import asyncio
import requests
import json
from pathlib import Path

# Add the ray directory to Python path
ray_dir = Path(__file__).parent.parent / "terraform" / "inference" / "ray"
sys.path.insert(0, str(ray_dir))

def test_health_check(base_url: str = "http://localhost:8000"):
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/-/healthz")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat_completion(base_url: str = "http://localhost:8000"):
    """Test the chat completion endpoint"""
    try:
        payload = {
            "model": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
            "messages": [
                {"role": "user", "content": "Hello! How are you today?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7,
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Chat completion successful!")
            print(f"📝 Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Ray Serve Chat Completion Service")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Service is not running or health check failed")
        return
    
    # Test chat completion
    if test_chat_completion():
        print("\n🎉 All tests passed! The service is working correctly.")
    else:
        print("\n❌ Chat completion test failed.")

if __name__ == "__main__":
    main()



