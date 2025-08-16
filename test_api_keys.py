#!/usr/bin/env python3
"""
Simple script to test if your API keys are properly configured
Run this to check if your external APIs will work
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_keys():
    """Test if all required API keys are present"""
    print("🔑 Testing API Key Configuration...")
    print("=" * 50)
    
    # Check each API key
    api_keys = {
        'OPENWEATHER_API_KEY': 'OpenWeatherMap (Weather Data)',
        'YOUTUBE_API_KEY': 'YouTube (Location Videos)',
        'GOOGLE_MAPS_API_KEY': 'Google Maps (Embed Maps)',
        'GOOGLE_PLACES_API_KEY': 'Google Places (Nearby Places)'
    }
    
    all_good = True
    
    for key_name, description in api_keys.items():
        api_key = os.getenv(key_name)
        if api_key:
            print(f"✅ {key_name}: {description} - CONFIGURED")
            print(f"   Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
        else:
            print(f"❌ {key_name}: {description} - MISSING")
            all_good = False
        print()
    
    if all_good:
        print("🎉 All API keys are configured! Your external APIs should work.")
    else:
        print("⚠️  Some API keys are missing. Please add them to your .env file:")
        print()
        print("Create a .env file in your backend directory with:")
        print("OPENWEATHER_API_KEY=your_openweather_api_key")
        print("YOUTUBE_API_KEY=your_youtube_api_key")
        print("GOOGLE_MAPS_API_KEY=your_google_maps_api_key")
        print("GOOGLE_PLACES_API_KEY=your_google_places_api_key")
        print()
        print("You can get these API keys from:")
        print("- OpenWeatherMap: https://openweathermap.org/api")
        print("- YouTube: https://console.cloud.google.com/apis/library/youtube.googleapis.com")
        print("- Google Maps/Places: https://console.cloud.google.com/apis/library/places-backend.googleapis.com")

if __name__ == "__main__":
    test_api_keys()
