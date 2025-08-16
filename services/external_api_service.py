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
                # Return mock data when API key is not configured
                print(f"⚠️ YouTube API key not configured, returning mock data for {location}")
                mock_videos = [
                     {
                         'id': 'mock_video_1',
                         'title': f'Amazing {location} - Travel Guide',
                         'description': f'Discover the best attractions and hidden gems in {location}',
                         'thumbnail': 'https://via.placeholder.com/320x180/87CEEB/ffffff?text=Travel+Guide',
                         'channel_title': 'Travel Explorer',
                         'published_at': '2024-01-01T00:00:00Z',
                         'url': f'https://www.youtube.com/watch?v=mock_video_1'
                     },
                     {
                         'id': 'mock_video_2',
                         'title': f'{location} Tourism - Must Visit Places',
                         'description': f'Top tourist attractions and landmarks in {location}',
                         'thumbnail': 'https://via.placeholder.com/320x180/4682B4/ffffff?text=Tourism',
                         'channel_title': 'Tourism Guide',
                         'published_at': '2024-01-02T00:00:00Z',
                         'url': f'https://www.youtube.com/watch?v=mock_video_2'
                     },
                     {
                         'id': 'mock_video_3',
                         'title': f'{location} City Tour - Local Experience',
                         'description': f'Experience {location} like a local with this comprehensive city tour',
                         'thumbnail': 'https://via.placeholder.com/320x180/20B2AA/ffffff?text=City+Tour',
                         'channel_title': 'Local Explorer',
                         'published_at': '2024-01-03T00:00:00Z',
                         'url': f'https://www.youtube.com/watch?v=mock_video_3'
                     }
                 ]
                return True, mock_videos[:max_results], None
            
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
                # Return mock data when API key is not configured
                print(f"⚠️ Google Places API key not configured, returning mock data for {place_type}")
                mock_places = []
                
                if place_type == 'restaurant':
                      mock_places = [
                          {
                              'place_id': 'mock_restaurant_1',
                              'name': 'The Grand Bistro',
                              'formatted_address': '123 Main Street, Downtown',
                              'rating': 4.8,
                              'user_ratings_total': 2847,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.001, 'lng': longitude + 0.001}},
                              'photos': [{'photo_reference': 'mock_photo_1', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/FF6B6B/ffffff?text=The+Grand+Bistro',
                              'formatted_phone_number': '+1 (555) 123-4567',
                              'website': 'https://grandbistro.example.com',
                              'opening_hours': {'open_now': True}
                          },
                                                   {
                              'place_id': 'mock_restaurant_2',
                              'name': 'Café Central',
                              'formatted_address': '456 Oak Avenue, Midtown',
                              'rating': 4.6,
                              'user_ratings_total': 2156,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.001, 'lng': longitude + 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_2', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/4ECDC4/ffffff?text=Café+Central',
                              'formatted_phone_number': '+1 (555) 987-6543',
                              'website': 'https://cafecentral.example.com',
                              'opening_hours': {'open_now': False}
                          },
                                                   {
                              'place_id': 'mock_restaurant_3',
                              'name': 'Pizza Palace',
                              'formatted_address': '789 Pine Street, Downtown',
                              'rating': 4.4,
                              'user_ratings_total': 1892,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.002, 'lng': longitude - 0.001}},
                              'photos': [{'photo_reference': 'mock_photo_3', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/45B7D1/ffffff?text=Pizza+Palace',
                              'formatted_phone_number': '+1 (555) 456-7890',
                              'website': 'https://pizzapalace.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_restaurant_4',
                              'name': 'Sushi Master',
                              'formatted_address': '321 Elm Street, Midtown',
                              'rating': 4.7,
                              'user_ratings_total': 1654,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.002, 'lng': longitude - 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_4', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/96CEB4/ffffff?text=Sushi+Master',
                              'formatted_phone_number': '+1 (555) 321-6540',
                              'website': 'https://sushimaster.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_restaurant_5',
                              'name': 'Burger House',
                              'formatted_address': '654 Maple Drive, Downtown',
                              'rating': 4.3,
                              'user_ratings_total': 1432,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.003, 'lng': longitude + 0.003}},
                              'photos': [{'photo_reference': 'mock_photo_5', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/FECA57/ffffff?text=Burger+House',
                              'formatted_phone_number': '+1 (555) 789-0123',
                              'website': 'https://burgerhouse.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_restaurant_6',
                              'name': 'Taco Fiesta',
                              'formatted_address': '987 Cedar Lane, Midtown',
                              'rating': 4.5,
                              'user_ratings_total': 1287,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.003, 'lng': longitude + 0.001}},
                              'photos': [{'photo_reference': 'mock_photo_6', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/FF9FF3/ffffff?text=Taco+Fiesta',
                              'formatted_phone_number': '+1 (555) 654-3210',
                              'website': 'https://tacofiesta.example.com',
                              'opening_hours': {'open_now': False}
                          },
                          {
                              'place_id': 'mock_restaurant_7',
                              'name': 'Pasta Paradise',
                              'formatted_address': '147 Birch Road, Downtown',
                              'rating': 4.2,
                              'user_ratings_total': 1156,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.004, 'lng': longitude - 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_7', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/54A0FF/ffffff?text=Pasta+Paradise',
                              'formatted_phone_number': '+1 (555) 147-2580',
                              'website': 'https://pastaparadise.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_restaurant_8',
                              'name': 'Steak House',
                              'formatted_address': '258 Willow Way, Midtown',
                              'rating': 4.6,
                              'user_ratings_total': 987,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.004, 'lng': longitude - 0.003}},
                              'photos': [{'photo_reference': 'mock_photo_8', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/5F27CD/ffffff?text=Steak+House',
                              'formatted_phone_number': '+1 (555) 258-3690',
                              'website': 'https://steakhouse.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_restaurant_9',
                              'name': 'Seafood Delight',
                              'formatted_address': '369 Spruce Street, Downtown',
                              'rating': 4.4,
                              'user_ratings_total': 876,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.005, 'lng': longitude + 0.004}},
                              'photos': [{'photo_reference': 'mock_photo_9', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/00D2D3/ffffff?text=Seafood+Delight',
                              'formatted_phone_number': '+1 (555) 369-1470',
                              'website': 'https://seafooddelight.example.com',
                              'opening_hours': {'open_now': False}
                          },
                          {
                              'place_id': 'mock_restaurant_10',
                              'name': 'Dessert Corner',
                              'formatted_address': '741 Poplar Avenue, Midtown',
                              'rating': 4.3,
                              'user_ratings_total': 765,
                              'types': ['restaurant', 'food', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.005, 'lng': longitude + 0.005}},
                              'photos': [{'photo_reference': 'mock_photo_10', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/FF6B6B/ffffff?text=Dessert+Corner',
                              'formatted_phone_number': '+1 (555) 741-8520',
                              'website': 'https://dessertcorner.example.com',
                              'opening_hours': {'open_now': True}
                          }
                     ]
                elif place_type == 'hospital':
                    mock_places = [
                          {
                              'place_id': 'mock_hospital_1',
                              'name': 'City General Hospital',
                              'formatted_address': '789 Health Boulevard, Medical District',
                              'rating': 4.8,
                              'user_ratings_total': 2847,
                              'types': ['hospital', 'health', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.002, 'lng': longitude - 0.001}},
                              'photos': [{'photo_reference': 'mock_photo_3', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/E74C3C/ffffff?text=City+General+Hospital',
                              'formatted_phone_number': '+1 (555) 911-0000',
                              'website': 'https://citygeneralhospital.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_hospital_2',
                              'name': 'Regional Medical Center',
                              'formatted_address': '456 Medical Drive, Healthcare District',
                              'rating': 4.6,
                              'user_ratings_total': 2156,
                              'types': ['hospital', 'health', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.002, 'lng': longitude + 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_4', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/3498DB/ffffff?text=Regional+Medical+Center',
                              'formatted_phone_number': '+1 (555) 911-1111',
                              'website': 'https://regionalmedical.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_hospital_3',
                              'name': 'Emergency Care Clinic',
                              'formatted_address': '123 Emergency Lane, Medical District',
                              'rating': 4.4,
                              'user_ratings_total': 1892,
                              'types': ['hospital', 'health', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.003, 'lng': longitude + 0.003}},
                              'photos': [{'photo_reference': 'mock_photo_5', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/F39C12/ffffff?text=Emergency+Care+Clinic',
                              'formatted_phone_number': '+1 (555) 911-2222',
                              'website': 'https://emergencycare.example.com',
                              'opening_hours': {'open_now': True}
                          }
                     ]
                elif place_type == 'lodging':
                    mock_places = [
                          {
                              'place_id': 'mock_hotel_1',
                              'name': 'Grand Hotel & Spa',
                              'formatted_address': '321 Comfort Lane, Luxury District',
                              'rating': 4.7,
                              'user_ratings_total': 2847,
                              'types': ['lodging', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.002, 'lng': longitude - 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_4', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/9B59B6/ffffff?text=Grand+Hotel+%26+Spa',
                              'formatted_phone_number': '+1 (555) 777-8888',
                              'website': 'https://grandhotel.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_hotel_2',
                              'name': 'Business Inn',
                              'formatted_address': '654 Corporate Drive, Business District',
                              'rating': 4.5,
                              'user_ratings_total': 2156,
                              'types': ['lodging', 'establishment'],
                              'geometry': {'location': {'lat': latitude + 0.002, 'lng': longitude + 0.002}},
                              'photos': [{'photo_reference': 'mock_photo_5', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/34495E/ffffff?text=Business+Inn',
                              'formatted_phone_number': '+1 (555) 777-9999',
                              'website': 'https://businessinn.example.com',
                              'opening_hours': {'open_now': True}
                          },
                          {
                              'place_id': 'mock_hotel_3',
                              'name': 'Comfort Suites',
                              'formatted_address': '987 Relaxation Road, Comfort District',
                              'rating': 4.3,
                              'user_ratings_total': 1892,
                              'types': ['lodging', 'establishment'],
                              'geometry': {'location': {'lat': latitude - 0.003, 'lng': longitude + 0.003}},
                              'photos': [{'photo_reference': 'mock_photo_6', 'height': 400, 'width': 600}],
                              'photo_url': 'https://via.placeholder.com/400x300/1ABC9C/ffffff?text=Comfort+Suites',
                              'formatted_phone_number': '+1 (555) 777-7777',
                              'website': 'https://comfortsuites.example.com',
                              'opening_hours': {'open_now': True}
                          }
                     ]
                
                return True, mock_places, None
            
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
    
    def get_place_details(self, place_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get detailed information about a specific place
        """
        try:
            if not self.google_places_api_key:
                return False, None, "Google Places API key not configured"
            
            details_url = f"{self.google_places_base_url}/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,opening_hours,photos,reviews',
                'key': self.google_places_api_key
            }
            
            response = requests.get(details_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"Google Places Details API error: {response.status_code}"
            
            data = response.json()
            place_details = data.get('result', {})
            
            return True, place_details, None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Google Places Details API request error: {str(e)}"
        except Exception as e:
            return False, None, f"Place details error: {str(e)}"
    
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
    
    def get_location_suggestions(self, query: str, max_results: int = 5) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Get location suggestions using Google Places Autocomplete API
        """
        try:
            if not self.google_places_api_key:
                return False, None, "Google Places API key not configured"
            
            autocomplete_url = f"{self.google_places_base_url}/autocomplete/json"
            params = {
                'input': query,
                'types': '(cities)',
                'key': self.google_places_api_key
            }
            
            response = requests.get(autocomplete_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"Google Places Autocomplete API error: {response.status_code}"
            
            data = response.json()
            suggestions = []
            
            for prediction in data.get('predictions', [])[:max_results]:
                suggestion = {
                    'place_id': prediction.get('place_id'),
                    'description': prediction.get('description'),
                    'structured_formatting': prediction.get('structured_formatting', {}),
                    'types': prediction.get('types', [])
                }
                suggestions.append(suggestion)
            
            return True, suggestions, None
            
        except requests.exceptions.RequestException as e:
            return False, None, f"Google Places Autocomplete API request error: {str(e)}"
        except Exception as e:
            return False, None, f"Location suggestions error: {str(e)}"
    
    def get_geocoding_info(self, address: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get geocoding information for an address
        """
        try:
            if not self.google_maps_api_key:
                return False, None, "Google Maps API key not configured"
            
            geocoding_url = f"{self.google_maps_base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.google_maps_api_key
            }
            
            response = requests.get(geocoding_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"Google Geocoding API error: {response.status_code}"
            
            data = response.json()
            
            if data.get('results'):
                result = data['results'][0]
                geocoding_info = {
                    'formatted_address': result.get('formatted_address'),
                    'geometry': result.get('geometry', {}),
                    'place_id': result.get('place_id'),
                    'types': result.get('types', []),
                    'address_components': result.get('address_components', [])
                }
                return True, geocoding_info, None
            else:
                return False, None, "No geocoding results found"
                
        except requests.exceptions.RequestException as e:
            return False, None, f"Google Geocoding API request error: {str(e)}"
        except Exception as e:
            return False, None, f"Geocoding error: {str(e)}"
    
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
