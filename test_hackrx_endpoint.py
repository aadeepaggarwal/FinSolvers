#!/usr/bin/env python3
"""
Test Script for HackRx 6.0 API Endpoint

Tests the /api/v1/hackrx/run endpoint with sample data to ensure
it matches the exact format required by the hackathon platform.
"""

import requests
import json

def test_hackrx_endpoint():
    """Test the HackRx API endpoint locally."""
    
    # Test data matching the hackathon format
    test_data = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?"
        ]
    }
    
    # Headers as required by the hackathon
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer test-api-key'
    }
    
    # Test against local server
    local_url = "http://localhost:5001/api/v1/hackrx/run"
    
    try:
        print("🧪 Testing HackRx API endpoint...")
        print(f"📍 URL: {local_url}")
        print(f"📄 Questions: {len(test_data['questions'])}")
        
        response = requests.post(
            local_url,
            json=test_data,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got {len(result.get('answers', []))} answers")
            print("\n📋 Sample Response:")
            print(json.dumps(result, indent=2)[:500] + "..." if len(json.dumps(result, indent=2)) > 500 else json.dumps(result, indent=2))
            
            # Validate response format
            if 'answers' in result and isinstance(result['answers'], list):
                print(f"✅ Response format is correct")
                print(f"📊 Expected {len(test_data['questions'])} answers, got {len(result['answers'])}")
            else:
                print("❌ Response format is incorrect")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the Flask server is running:")
        print("   python flask_app.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_health_endpoint():
    """Test the health check endpoint."""
    try:
        response = requests.get("http://localhost:5001/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"📊 Service: {response.json().get('service', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    print("🚀 HackRx 6.0 API Endpoint Test")
    print("=" * 40)
    
    # Test health endpoint first
    test_health_endpoint()
    print()
    
    # Test main API endpoint
    test_hackrx_endpoint()
    
    print("\n🎯 Ready for submission!")
    print("📝 Webhook URL: http://localhost:5001/api/v1/hackrx/run")
    print("🌐 Deploy to Heroku/Railway/Vercel for public access")
