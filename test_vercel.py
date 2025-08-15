#!/usr/bin/env python3
"""
Test script for NeverPay2Spotify Vercel deployment
"""

import requests
import json
import sys

def test_vercel_deployment(base_url):
    """Test the Vercel deployment"""
    print(f"Testing deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Check if the main page loads
    print("1. Testing main page...")
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            if "NeverPay2Spotify" in response.text:
                print("✅ HTML content contains app title")
            else:
                print("⚠️  HTML content might be different than expected")
        else:
            print(f"❌ Main page failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading main page: {e}")
        return False
    
    # Test 2: Test the transfer endpoint with invalid data
    print("\n2. Testing transfer endpoint...")
    try:
        test_data = {
            "spotify_url": "https://open.spotify.com/playlist/invalid",
            "ytmusic_headers": {"test": "invalid"},
            "spotify_client_id": None,
            "spotify_client_secret": None
        }
        
        response = requests.post(
            f"{base_url}/transfer",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print("✅ Transfer endpoint responds correctly with error")
                print(f"   Error message: {result['error']}")
            else:
                print("⚠️  Transfer endpoint responded but no error in response")
        else:
            print(f"❌ Transfer endpoint failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error testing transfer endpoint: {e}")
    
    # Test 3: Test CORS headers
    print("\n3. Testing CORS headers...")
    try:
        response = requests.options(base_url, timeout=10)
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print("✅ CORS headers are present")
        else:
            print("⚠️  CORS headers might be missing")
    except Exception as e:
        print(f"❌ Error testing CORS: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic deployment test completed!")
    print("\nNext steps:")
    print("1. Get your YouTube Music headers using 'ytmusicapi setup'")
    print("2. Try transferring a real Spotify playlist")
    print("3. Check the Vercel function logs if you encounter issues")
    
    return True

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter your Vercel deployment URL (e.g., https://your-app.vercel.app): ").strip()
    
    if not base_url.startswith(('http://', 'https://')):
        base_url = f"https://{base_url}"
    
    if not base_url.endswith('/'):
        base_url += '/'
    
    test_vercel_deployment(base_url)

if __name__ == "__main__":
    main()
