#!/usr/bin/env python3
"""
Test script to diagnose YouTube API issues
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_youtube_api():
    """Test YouTube API connectivity and key validity"""
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    print("🔍 YouTube API Diagnostic Test")
    print("=" * 50)
    
    # Check if API key exists
    if not youtube_api_key:
        print("❌ ERROR: YOUTUBE_API_KEY not found in environment variables")
        print("   Make sure you have a .env file with YOUTUBE_API_KEY=your_key")
        return False
    
    print(f"✅ API Key found: {youtube_api_key[:10]}...{youtube_api_key[-4:]}")
    
    # Test basic API call
    try:
        print("\n🔍 Testing YouTube API connectivity...")
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            params={
                'part': 'snippet',
                'q': 'test',
                'type': 'video',
                'maxResults': 1,
                'key': youtube_api_key
            },
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ YouTube API is working correctly!")
            print(f"   Found {len(data.get('items', []))} videos")
            return True
            
        elif response.status_code == 403:
            print("❌ 403 Forbidden Error")
            try:
                error_data = response.json()
                error_info = error_data.get('error', {})
                print(f"   Error Code: {error_info.get('code', 'Unknown')}")
                print(f"   Error Message: {error_info.get('message', 'Unknown')}")
                
                # Check specific error reasons
                if 'quota' in error_info.get('message', '').lower():
                    print("   💡 This appears to be a quota limit issue")
                    print("   💡 Check your YouTube API quota in Google Cloud Console")
                elif 'key' in error_info.get('message', '').lower():
                    print("   💡 This appears to be an API key issue")
                    print("   💡 Check if your API key is valid and has YouTube Data API v3 enabled")
                elif 'disabled' in error_info.get('message', '').lower():
                    print("   💡 YouTube Data API v3 might be disabled")
                    print("   💡 Enable it in Google Cloud Console")
                    
            except Exception as e:
                print(f"   Could not parse error details: {e}")
            return False
            
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_api_requirements():
    """Check what's needed for YouTube API"""
    print("\n📋 YouTube API Requirements:")
    print("=" * 50)
    print("1. ✅ Google Cloud Project")
    print("2. ✅ YouTube Data API v3 enabled")
    print("3. ✅ API Key with YouTube Data API v3 access")
    print("4. ✅ Sufficient quota (10,000 units/day free)")
    print("5. ✅ API key restrictions (if any) allow your domain/IP")
    
    print("\n🔗 Useful Links:")
    print("- Google Cloud Console: https://console.cloud.google.com/")
    print("- YouTube Data API v3: https://developers.google.com/youtube/v3")
    print("- API Quotas: https://console.cloud.google.com/apis/credentials")

if __name__ == "__main__":
    success = test_youtube_api()
    check_api_requirements()
    
    if not success:
        print("\n🚨 To fix YouTube API issues:")
        print("1. Go to Google Cloud Console")
        print("2. Enable YouTube Data API v3")
        print("3. Create/update API key with proper permissions")
        print("4. Check quota limits")
        print("5. Update your .env file with the correct API key")
