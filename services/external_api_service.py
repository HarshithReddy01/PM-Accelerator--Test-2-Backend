import requests
import json
from typing import Dict, List, Optional, Tuple
import os

class ExternalAPIService:
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        
        # API endpoints
        self.youtube_base_url = 'https://www.googleapis.com/youtube/v3'
        self.google_maps_base_url = 'https://maps.googleapis.com/maps/api'
        self.google_places_base_url = 'https://maps.googleapis.com/maps/api/place'
    
    def get_youtube_videos(self, location: str, max_results: int = 5) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Get YouTube videos related to the location
        """
        try:
            if not self.youtube_api_key:
                return False, None, "YouTube API key not configured"
            
            # Search for location-related videos
            search_url = f"{self.youtube_base_url}/search"
            params = {
                'part': 'snippet',
                'q': f"{location} travel tourism attractions",
                'type': 'video',
                'maxResults': max_results,
                'key': self.youtube_api_key,
                'order': 'relevance'
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"YouTube API error: {response.status_code}"
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_info = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                videos.append(video_info)
            
            return True, videos, None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"YouTube API request error: {str(e)}"
        except Exception as e:
            return False, None, f"YouTube videos error: {str(e)}"
    
    def get_google_maps_embed_url(self, latitude: float, longitude: float, zoom: int = 12) -> str:
        """
        Generate Google Maps embed URL
        """
        try:
            if not self.google_maps_api_key:
                return f"https://maps.google.com/maps?q={latitude},{longitude}&z={zoom}&output=embed"
            
            return f"https://www.google.com/maps/embed/v1/view?key={self.google_maps_api_key}&center={latitude},{longitude}&zoom={zoom}"
            
        except Exception as e:
            # Fallback to basic embed URL
            return f"https://maps.google.com/maps?q={latitude},{longitude}&z={zoom}&output=embed"
    
    def get_nearby_places(self, latitude: float, longitude: float, radius: int = 5000, 
                         place_type: str = 'restaurant') -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Get nearby places using Google Places API
        """
        try:
            if not self.google_places_api_key:
                return False, None, "Google Places API key not configured"
            
            # Search for nearby places using exact Google Places API format
            search_url = f"{self.google_places_base_url}/nearbysearch/json"
            params = {
                 'location': f"{latitude},{longitude}",
                 'radius': radius,
                 'type': place_type,
                 'key': self.google_places_api_key,
                 'rankby': 'prominence'  # This will sort by prominence (most reviewed/popular first)
             }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"Google Places API error: {response.status_code}"
            
            data = response.json()
            places = []
            
            # Limit results to 10 places
            for place in data.get('results', [])[:10]:
                # Get photo URL if available
                photo_url = None
                if place.get('photos') and len(place['photos']) > 0:
                    photo_reference = place['photos'][0]['photo_reference']
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={self.google_places_api_key}"
                
                place_info = {
                     'place_id': place.get('place_id'),
                     'name': place.get('name'),
                     'formatted_address': place.get('vicinity'),  # Use vicinity as formatted_address
                     'rating': place.get('rating'),
                     'user_ratings_total': place.get('user_ratings_total'),
                     'types': place.get('types', []),
                     'geometry': place.get('geometry', {}),
                     'photos': place.get('photos', []),
                     'photo_url': photo_url,  # Add the actual photo URL
                     'formatted_phone_number': place.get('formatted_phone_number'),
                     'website': place.get('website'),
                     'opening_hours': place.get('opening_hours', {})
                }
                places.append(place_info)
            
            return True, places, None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Google Places API request error: {str(e)}"
        except Exception as e:
            return False, None, f"Nearby places error: {str(e)}"
    

    
    def get_multiple_place_types(self, latitude: float, longitude: float, 
                                place_types: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Get multiple types of nearby places
        """
        if place_types is None:
            place_types = ['restaurant', 'hospital', 'lodging']
        
        results = {}
        
        for place_type in place_types:
            success, places, error = self.get_nearby_places(latitude, longitude, place_type=place_type)
            if success:
                results[place_type] = places
            else:
                results[place_type] = []
                print(f"Error fetching {place_type}: {error}")
        
        return results
    

    
    def get_reverse_geocoding(self, latitude: float, longitude: float) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get reverse geocoding information from coordinates
        """
        try:
            if not self.google_maps_api_key:
                return False, None, "Google Maps API key not configured"
            
            reverse_geocoding_url = f"{self.google_maps_base_url}/geocode/json"
            params = {
                'latlng': f"{latitude},{longitude}",
                'key': self.google_maps_api_key
            }
            
            response = requests.get(reverse_geocoding_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"Google Reverse Geocoding API error: {response.status_code}"
            
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                reverse_geocoding_info = {
                    'formatted_address': result.get('formatted_address'),
                    'geometry': result.get('geometry', {}),
                    'place_id': result.get('place_id'),
                    'types': result.get('types', []),
                    'address_components': result.get('address_components', [])
                }
                return True, reverse_geocoding_info, None
            else:
                return False, None, "No reverse geocoding results found"
                
        except requests.exceptions.RequestException as e:
            return False, None, f"Google Reverse Geocoding API request error: {str(e)}"
        except Exception as e:
            return False, None, f"Reverse geocoding error: {str(e)}"
