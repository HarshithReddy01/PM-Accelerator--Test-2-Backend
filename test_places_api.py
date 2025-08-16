#!/usr/bin/env python3
"""
Test script to verify Google Places API is working with real photos
"""

import os
from dotenv import load_dotenv
from services.external_api_service import ExternalAPIService

# Load environment variables
load_dotenv()

def test_places_api():
    """Test Google Places API with real photos"""
    print("🧪 Testing Google Places API with Real Photos...")
    print("=" * 60)
    
    # Check if API key is set
    if not os.getenv('GOOGLE_PLACES_API_KEY'):
        print("⚠️  Google Places API key not found in environment variables")
        return
    
    service = ExternalAPIService()
    
    # Test coordinates (New York City)
    latitude = 40.7128
    longitude = -74.0060
    
    print(f"📍 Testing nearby places around: {latitude}, {longitude}")
    print()
    
    # Test different place types
    place_types = ['restaurant', 'hospital', 'lodging']
    
    for place_type in place_types:
        print(f"🔍 Searching for {place_type}s...")
        
        success, places, error = service.get_nearby_places(
            latitude=latitude, 
            longitude=longitude, 
            radius=5000, 
            place_type=place_type
        )
        
        if success and places:
            print(f"✅ Found {len(places)} {place_type}s")
            
            # Check if we have real photos
            real_photos = 0
            placeholder_photos = 0
            
            for place in places[:3]:  # Check first 3 places
                if place.get('photo_url'):
                    if 'maps.googleapis.com' in place['photo_url']:
                        real_photos += 1
                        print(f"   📸 {place['name']}: REAL PHOTO")
                    elif 'placeholder.com' in place['photo_url']:
                        placeholder_photos += 1
                        print(f"   🖼️  {place['name']}: PLACEHOLDER")
                    else:
                        print(f"   ❓ {place['name']}: UNKNOWN PHOTO TYPE")
                else:
                    print(f"   ❌ {place['name']}: NO PHOTO")
            
            print(f"   📊 Real photos: {real_photos}, Placeholders: {placeholder_photos}")
            
        else:
            print(f"❌ Error fetching {place_type}s: {error}")
        
        print()
    
    print("🎯 Test completed!")

if __name__ == "__main__":
    test_places_api()
