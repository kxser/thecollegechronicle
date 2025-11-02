#!/usr/bin/env python3
"""
Demo script to test the Article Generator Web Server API
"""

import json
import requests
import time

def test_server():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Article Generator Web Server...")
    
    # Test health endpoint
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check failed")
            return
    except requests.RequestException as e:
        print(f"❌ Could not connect to server: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        return
    
    # Test models endpoint
    print("\n2. Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/api/models")
        if response.status_code == 200:
            models = response.json()
            print("✅ Models endpoint working")
            print(f"   Available models: {models['models']}")
        else:
            print("❌ Models endpoint failed")
    except requests.RequestException as e:
        print(f"❌ Models endpoint error: {e}")
    
    # Test article processing (with a simple example)
    print("\n3. Testing article processing...")
    test_article = {
        "articles": [
            {
                "title": "Test Article",
                "author": "Demo User",
                "date": "2025-01-15",
                "category": "misc",
                "body": "This is a test article to verify that the AI processing works correctly. The system should format this text properly and create a markdown file with appropriate front matter."
            }
        ],
        "model_name": "gemini-2.5-pro"
    }
    
    try:
        print("   Sending test article to AI...")
        response = requests.post(
            f"{base_url}/api/process-articles",
            json=test_article,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Article processing successful!")
                print(f"   Files created: {result.get('files_created', [])}")
                if result.get('raw_response'):
                    print("   AI response preview:")
                    preview = result['raw_response'][:200] + "..." if len(result['raw_response']) > 200 else result['raw_response']
                    print(f"   {preview}")
            else:
                print(f"❌ Article processing failed: {result.get('error_message')}")
        else:
            print(f"❌ Article processing request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Article processing error: {e}")
    
    print("\n🎉 Testing complete!")
    print("\nTo use the web interface:")
    print("1. Open your browser")
    print("2. Navigate to http://localhost:8000")
    print("3. Fill in the form and create articles")

if __name__ == "__main__":
    test_server()