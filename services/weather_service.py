import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from models import WeatherRecord
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import os

class WeatherService:
    def __init__(self):
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.openweather_base_url = 'https://api.openweathermap.org/data/2.5'
        self.geolocator = Nominatim(user_agent="weather_app")
        
    def validate_location(self, location: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Validate if a location exists and return coordinates
        """
        try:
            # Try to geocode the location
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
            
            # Check if start date is in the past
            if start < today:
                return False, "Start date cannot be in the past"
            
            # Check if end date is before start date
            if end < start:
                return False, "End date must be after start date"
            
            # Check if date range exceeds 7 days
            days_diff = (end - start).days
            if days_diff > 7:
                return False, "Date range cannot exceed 7 days"
            
            return True, None
            
        except ValueError as e:
            return False, f"Invalid date format: {str(e)}"
        except Exception as e:
            return False, f"Date validation error: {str(e)}"
    
    def fetch_weather_data(self, lat: float, lon: float, start_date: str, end_date: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Fetch weather data from OpenWeather API
        """
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
            
            # Get 5-day forecast
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
            
            # Debug logging
            if forecast_data.get('list'):
                first_item = forecast_data['list'][0]
                last_item = forecast_data['list'][-1]
                print(f"First forecast: {first_item.get('dt_txt')} - {datetime.fromtimestamp(first_item.get('dt'))}")
                print(f"Last forecast: {last_item.get('dt_txt')} - {datetime.fromtimestamp(last_item.get('dt'))}")
                
                # Check if we have enough data for 5 days
                forecast_dates = set()
                for item in forecast_data.get('list', []):
                    forecast_date = datetime.fromtimestamp(item.get('dt')).date()
                    forecast_dates.add(forecast_date)
                
                print(f"Unique forecast dates available: {len(forecast_dates)}")
                print(f"Available dates: {sorted(forecast_dates)}")
                
                # Log the available dates for debugging
                print(f"Available forecast dates: {sorted(forecast_dates)}")
                if len(forecast_dates) < 6:
                    print(f"Warning: Only {len(forecast_dates)} unique dates available, may not have enough data for 5-day forecast")
            
            # Combine current and forecast data
            weather_data = {
                'current': current_data,
                'forecast': forecast_data
            }
            
            return True, weather_data, None
            
        except Exception as e:
            return False, None, f"Weather data fetch error: {str(e)}"
    
    def create_weather_record(self, db: Session, location: str, start_date: str, end_date: str, 
                            latitude: float, longitude: float, temperature_data: Dict) -> Tuple[bool, Optional[WeatherRecord], Optional[str]]:
        """
        Create a new weather record in the database
        """
        try:
            weather_record = WeatherRecord(
                location=location,
                start_date=start_date,
                end_date=end_date,
                latitude=latitude,
                longitude=longitude,
                temperature_data=temperature_data
            )
            
            db.add(weather_record)
            db.commit()
            db.refresh(weather_record)
            
            return True, weather_record, None
            
        except Exception as e:
            db.rollback()
            return False, None, f"Database error: {str(e)}"
    
    def get_all_weather_records(self, db: Session) -> List[WeatherRecord]:
        """
        Get all weather records from database
        """
        return db.query(WeatherRecord).all()
    
    def get_weather_record_by_id(self, db: Session, record_id: int) -> Optional[WeatherRecord]:
        """
        Get a specific weather record by ID
        """
        return db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    
    def update_weather_record(self, db: Session, record_id: int, location: str, 
                            start_date: str, end_date: str) -> Tuple[bool, Optional[WeatherRecord], Optional[str]]:
        """
        Update a weather record
        """
        try:
            record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
            if not record:
                return False, None, "Weather record not found"
            
            # Validate location
            is_valid, location_data, error = self.validate_location(location)
            if not is_valid:
                return False, None, error
            
            # Validate date range
            is_valid, error = self.validate_date_range(start_date, end_date)
            if not is_valid:
                return False, None, error
            
            # Fetch new weather data
            is_valid, weather_data, error = self.fetch_weather_data(
                location_data['latitude'], 
                location_data['longitude'], 
                start_date, 
                end_date
            )
            if not is_valid:
                return False, None, error
            
            # Update record
            record.location = location
            record.start_date = start_date
            record.end_date = end_date
            record.latitude = location_data['latitude']
            record.longitude = location_data['longitude']
            record.temperature_data = weather_data
            record.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(record)
            
            return True, record, None
            
        except Exception as e:
            db.rollback()
            return False, None, f"Update error: {str(e)}"
    
    def delete_weather_record(self, db: Session, record_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a weather record
        """
        try:
            record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
            if not record:
                return False, "Weather record not found"
            
            db.delete(record)
            db.commit()
            
            return True, None
            
        except Exception as e:
            db.rollback()
            return False, f"Delete error: {str(e)}"
    
    def get_todays_weather_3hour(self, location: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Get today's weather with 3-hour intervals
        """
        try:
            # Validate location
            is_valid, location_data, error = self.validate_location(location)
            if not is_valid:
                return False, None, error
            
            # Fetch weather data
            is_valid, weather_data, error = self.fetch_weather_data(
                location_data['latitude'],
                location_data['longitude'],
                datetime.now().strftime('%Y-%m-%d'),
                (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            )
            if not is_valid:
                return False, None, error
            
            # Process 3-hour interval data
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
            
            # Calculate most common weather
            weather_counts = {}
            for item in hourly_data:
                weather_desc = item['description'].lower()
                weather_counts[weather_desc] = weather_counts.get(weather_desc, 0) + 1
            
            most_common_weather = max(weather_counts.items(), key=lambda x: x[1])[0] if weather_counts else "Unknown"
            
            # Get most descriptive weather
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
        """
        Get the most descriptive weather condition from hourly data
        """
        if not hourly_data:
            return "Mixed Conditions"
        
        # Priority order for weather descriptions
        priority_weather = [
            'thunderstorm', 'rain', 'snow', 'fog', 'mist', 'haze',
            'clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds'
        ]
        
        weather_counts = {}
        for item in hourly_data:
            desc = item['description'].lower()
            weather_counts[desc] = weather_counts.get(desc, 0) + 1
        
        # Find the most frequent weather with highest priority
        most_frequent = max(weather_counts.items(), key=lambda x: x[1])
        
        # Map generic terms to more descriptive ones
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
        
        # Check if we have a mapping for this weather
        for key, value in weather_mapping.items():
            if key in weather_desc:
                return value
        
        # Return capitalized description if no mapping found
        return weather_desc.title()
