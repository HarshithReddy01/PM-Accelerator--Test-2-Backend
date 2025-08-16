import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import os

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.openweather_base_url = 'https://api.openweathermap.org/data/2.5' #free paln- Harshith Reddy
        self.geolocator = Nominatim(user_agent="weather_app")
        
    def validate_location(self, location: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            location_data = self.geolocator.geocode(location, timeout=10)
            
            if location_data:
                return True, {
                    'latitude': location_data.latitude,
                    'longitude': location_data.longitude,
                    'display_name': location_data.address
                }, None
            else:
                return False, None, f"Location '{location}' not found"
                
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            return False, None, f"Geocoding service error: {str(e)}"
        except Exception as e:
            return False, None, f"Location validation error: {str(e)}"
    
    def validate_date_range(self, start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
        """
        Validate date range constraints
        """
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if start < today:
                return False, "Start date cannot be in the past"
            
            if end < start:
                return False, "End date must be after start date"
            days_diff = (end - start).days
            if days_diff > 7:
                return False, "Date range cannot exceed 7 days"
            
            return True, None
            
        except ValueError as e:
            return False, f"Invalid date format: {str(e)}"
        except Exception as e:
            return False, f"Date validation error: {str(e)}"
    
    def fetch_weather_data(self, lat: float, lon: float, start_date: str, end_date: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            # Get current weather
            current_response = requests.get(
                f"{self.openweather_base_url}/weather",
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_api_key,
                    'units': 'metric'
                }
            )
            
            if current_response.status_code != 200:
                return False, None, f"OpenWeather API current weather error: {current_response.status_code}"
            
            current_data = current_response.json()
            
            forecast_response = requests.get(
                f"{self.openweather_base_url}/forecast",
                params={
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_api_key,
                    'units': 'metric'
                }
            )
            
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                if len(forecast_data.get('list', [])) < 40:
                    print(f"First request returned {len(forecast_data.get('list', []))} items, trying with cnt parameter...")
                    forecast_response = requests.get(
                        f"{self.openweather_base_url}/forecast",
                        params={
                            'lat': lat,
                            'lon': lon,
                            'appid': self.openweather_api_key,
                            'units': 'metric',
                            'cnt': 40
                        }
                    )
            
            if forecast_response.status_code != 200:
                return False, None, f"OpenWeather API forecast error: {forecast_response.status_code}"
            
            forecast_data = forecast_response.json()
            
            if forecast_data.get('list'):
                first_item = forecast_data['list'][0]
                last_item = forecast_data['list'][-1]
                print(f"First forecast: {first_item.get('dt_txt')} - {datetime.fromtimestamp(first_item.get('dt'))}")
                print(f"Last forecast: {last_item.get('dt_txt')} - {datetime.fromtimestamp(last_item.get('dt'))}")
                
                forecast_dates = set()
                for item in forecast_data.get('list', []):
                    forecast_date = datetime.fromtimestamp(item.get('dt')).date()
                    forecast_dates.add(forecast_date)
                
                print(f"Unique forecast dates available: {len(forecast_dates)}")
                print(f"Available dates: {sorted(forecast_dates)}")
                
                print(f"Available forecast dates: {sorted(forecast_dates)}")
                if len(forecast_dates) < 6:
                    print(f"Warning: Only {len(forecast_dates)} unique dates available, may not have enough data for 5-day forecast")
            
            weather_data = {
                'current': current_data,
                'forecast': forecast_data
            }
            
            return True, weather_data, None
            
        except Exception as e:
            return False, None, f"Weather data fetch error: {str(e)}"
    

    
    def get_todays_weather_3hour(self, location: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            is_valid, location_data, error = self.validate_location(location)
            if not is_valid:
                return False, None, error
            
            is_valid, weather_data, error = self.fetch_weather_data(
                location_data['latitude'],
                location_data['longitude'],
                datetime.now().strftime('%Y-%m-%d'),
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            )
            if not is_valid:
                return False, None, error
            
            forecast_list = weather_data.get('forecast', {}).get('list', [])
            hourly_data = []
            
            for item in forecast_list:
                dt = datetime.fromtimestamp(item['dt'])
                hourly_data.append({
                    'time': dt.strftime('%H:%M'),
                    'date': dt.strftime('%Y-%m-%d'),
                    'temperature': round(item['main']['temp']),
                    'feels_like': round(item['main']['feels_like']),
                    'humidity': item['main']['humidity'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'weather_main': item['weather'][0]['main'],
                    'weather_id': item['weather'][0]['id']
                })
            
            weather_counts = {}
            for item in hourly_data:
                weather_desc = item['description'].lower()
                weather_counts[weather_desc] = weather_counts.get(weather_desc, 0) + 1
            
            most_common_weather = max(weather_counts.items(), key=lambda x: x[1])[0] if weather_counts else "Unknown"
            
            most_descriptive = self.get_most_descriptive_weather(hourly_data)
            
            result = {
                'location': location_data['display_name'],
                'coordinates': {
                    'lat': location_data['latitude'],
                    'lon': location_data['longitude']
                },
                'current_weather': weather_data.get('current'),
                'hourly_forecast': hourly_data,
                'most_common_weather': most_descriptive,
                'total_periods': len(hourly_data)
            }
            
            return True, result, None
            
        except Exception as e:
            return False, None, f"Today's weather error: {str(e)}"
    
    def get_most_descriptive_weather(self, hourly_data: List[Dict]) -> str:
        if not hourly_data:
            return "Mixed Conditions"
        
        priority_weather = [
            'thunderstorm', 'rain', 'snow', 'fog', 'mist', 'haze',
            'clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds'
        ]
        
        weather_counts = {}
        for item in hourly_data:
            desc = item['description'].lower()
            weather_counts[desc] = weather_counts.get(desc, 0) + 1
        
        most_frequent = max(weather_counts.items(), key=lambda x: x[1])
        
        weather_mapping = {
            'clouds': 'Partly Cloudy',
            'clear': 'Clear Sky',
            'rain': 'Light Rain',
            'snow': 'Light Snow',
            'thunderstorm': 'Thunderstorm',
            'drizzle': 'Light Drizzle',
            'mist': 'Misty',
            'fog': 'Foggy',
            'haze': 'Hazy'
        }
        
        weather_desc = most_frequent[0]
        
        for key, value in weather_mapping.items():
            if key in weather_desc:
                return value
        
        return weather_desc.title()
