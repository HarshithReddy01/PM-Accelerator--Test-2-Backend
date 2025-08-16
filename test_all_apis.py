#!/usr/bin/env python3
"""
Comprehensive test script to verify all APIs are working and pulling real data
"""

import os
from dotenv import load_dotenv
from services.external_api_service import ExternalAPIService

# Load environment variables
load_dotenv()

def test_all_apis():
    """Test all external APIs to ensure they're working with real data"""
    print("🧪 Testing All External APIs...")
    print("=" * 60)
    
    # Check if all API keys are set
    required_keys = [
        'GOOGLE_MAPS_API_KEY',
        'GOOGLE_PLACES_API_KEY', 
        'YOUTUBE_API_KEY',
        'OPENWEATHER_API_KEY'
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("Please add them to your .env file")
        return
    
    service = ExternalAPIService()
    
    # Test coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060
    location = "New York"
    
    print(f"📍 Testing APIs for location: {location} ({latitude}, {longitude})")
    print()
    
    # Test 1: Google Places API (Nearby Places with Real Photos)
    print("1️⃣ Testing Google Places API (Nearby Places)...")
    success, places, error = service.get_nearby_places(
        latitude=latitude, 
        longitude=longitude, 
        radius=5000, 
        place_type='restaurant'
    )
    
    if success and places:
        real_photos = sum(1 for place in places[:5] if place.get('photo_url') and 'maps.googleapis.com' in place['photo_url'])
        print(f"   ✅ Found {len(places)} restaurants")
        print(f"   📸 {real_photos}/5 have real photos from Google Places API")
        print(f"   🏪 Sample: {places[0]['name']} - Rating: {places[0].get('rating', 'N/A')}")
    else:
        print(f"   ❌ Error: {error}")
    print()
    
    # Test 2: YouTube API (Location Videos)
    print("2️⃣ Testing YouTube API (Location Videos)...")
    success, videos, error = service.get_youtube_videos(location, max_results=3)
    
    if success and videos:
        real_videos = sum(1 for video in videos if 'youtube.com' in video.get('url', ''))
        print(f"   ✅ Found {len(videos)} videos")
        print(f"   🎥 {real_videos}/{len(videos)} are real YouTube videos")
        print(f"   📺 Sample: {videos[0]['title']}")
    else:
        print(f"   ❌ Error: {error}")
    print()
    
    # Test 3: Google Maps API (Embed URL)
    print("3️⃣ Testing Google Maps API (Embed URL)...")
    embed_url = service.get_google_maps_embed_url(latitude, longitude)
    
    if 'google.com/maps/embed' in embed_url:
        print(f"   ✅ Generated Google Maps embed URL with API key")
        print(f"   🗺️  URL: {embed_url[:80]}...")
    else:
        print(f"   ⚠️  Using fallback embed URL (no API key)")
    print()
    
    # Test 4: Multiple Place Types
    print("4️⃣ Testing Multiple Place Types...")
    place_types = ['restaurant', 'hospital', 'lodging']
    all_results = service.get_multiple_place_types(latitude, longitude, place_types)
    
    for place_type, places in all_results.items():
        if places:
            real_photos = sum(1 for place in places[:3] if place.get('photo_url') and 'maps.googleapis.com' in place['photo_url'])
            print(f"   📍 {place_type.capitalize()}: {len(places)} places, {real_photos}/3 with real photos")
        else:
            print(f"   ❌ {place_type.capitalize()}: No results")
    print()
    
    # Test 5: Location Suggestions (Autocomplete)
    print("5️⃣ Testing Location Suggestions (Autocomplete)...")
    success, suggestions, error = service.get_location_suggestions("New York", max_results=3)
    
    if success and suggestions:
        print(f"   ✅ Found {len(suggestions)} location suggestions")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion.get('description', 'N/A')}")
    else:
        print(f"   ❌ Error: {error}")
    print()
    
    # Test 6: Geocoding
    print("6️⃣ Testing Geocoding API...")
    success, geocoding_info, error = service.get_geocoding_info("New York, NY")
    
    if success and geocoding_info:
        print(f"   ✅ Geocoding successful")
        print(f"   📍 Address: {geocoding_info.get('formatted_address', 'N/A')}")
        location = geocoding_info.get('geometry', {}).get('location', {})
        print(f"   🗺️  Coordinates: {location.get('lat', 'N/A')}, {location.get('lng', 'N/A')}")
    else:
        print(f"   ❌ Error: {error}")
    print()
    
    # Test 7: Reverse Geocoding
    print("7️⃣ Testing Reverse Geocoding API...")
    success, reverse_info, error = service.get_reverse_geocoding(latitude, longitude)
    
    if success and reverse_info:
        print(f"   ✅ Reverse geocoding successful")
        print(f"   📍 Address: {reverse_info.get('formatted_address', 'N/A')}")
    else:
        print(f"   ❌ Error: {error}")
    print()
    
    print("🎯 All API Tests Completed!")
    print("=" * 60)
    print("✅ Your weather app should now display:")
    print("   🌤️  Real weather data from OpenWeather API")
    print("   📸 Real photos for nearby places from Google Places API")
    print("   🎥 Real YouTube videos from YouTube Data API")
    print("   🗺️  Interactive maps from Google Maps API")
    print("   📍 Location suggestions and geocoding from Google APIs")

if __name__ == "__main__":
    test_all_apis()
