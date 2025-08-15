from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import requests
import json
import csv
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}
db = SQLAlchemy(app)

# Google Maps Platform API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

# OpenWeather API Key
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'ec784b133d32aafc9a94a859ab777fa5')

# API Base URLs
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
GOOGLE_PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place"

# Weather Database Model
class WeatherRecord(db.Model):
    __tablename__ = 'weather_records'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    temperature_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def validate_date_range(start_date, end_date):
    """Validate date range"""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start > end:
            return False, "Start date cannot be after end date"
        
        if start < datetime.now().date() - timedelta(days=365):
            return False, "Start date cannot be more than 1 year in the past"
        
        if end > datetime.now().date() + timedelta(days=7):
            return False, "End date cannot be more than 7 days in the future"
        
        return True, (start, end)
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD"

def validate_location(location):
    """Validate and geocode location"""
    try:
        geolocator = Nominatim(user_agent="weather_app")
        location_data = geolocator.geocode(location, timeout=10)
        
        if location_data:
            return True, {
                'latitude': location_data.latitude,
                'longitude': location_data.longitude,
                'address': location_data.address
            }
        else:
            return False, "Location not found"
    except (GeocoderTimedOut, GeocoderUnavailable):
        return False, "Location service unavailable"







def get_weather_data(lat, lon, start_date, end_date):
    """Fetch weather data for a location and date range using OpenWeather API"""
    try:
        
        # Get current weather
        current_response = requests.get(
            f"{OPENWEATHER_BASE_URL}/weather",
            params={
                'lat': lat,
                'lon': lon,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
        )
        
        if current_response.status_code != 200:
            return None, f"OpenWeather API current weather error: {current_response.status_code}"
        
        current_data = current_response.json()

        # Get 5-day forecast (OpenWeather provides 3-hour intervals for 5 days)
        forecast_response = requests.get(
            f"{OPENWEATHER_BASE_URL}/forecast",
            params={
                'lat': lat,
                'lon': lon,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
        )
        
        if forecast_response.status_code != 200:
            return None, f"OpenWeather API forecast error: {forecast_response.status_code}"
        
        forecast_data = forecast_response.json()

        # Convert OpenWeather API format to our expected format
        current_weather = {
            'name': current_data.get('name', 'Current Location'),
            'sys': current_data.get('sys', {'country': 'US'}),
            'coord': current_data.get('coord', {'lat': lat, 'lon': lon}),
            'main': current_data.get('main', {}),
            'weather': current_data.get('weather', []),
            'wind': current_data.get('wind', {}),
            'visibility': current_data.get('visibility', 0),
            'dt': current_data.get('dt', int(datetime.now().timestamp()))
        }

        # Convert forecast data to our format (OpenWeather provides 3-hour intervals)
        forecast_list = []
        for forecast_item in forecast_data.get('list', []):
            timestamp = forecast_item.get('dt')
            if timestamp:
                forecast_datetime = datetime.fromtimestamp(timestamp)
                forecast_list.append({
                    'dt': int(forecast_datetime.timestamp()),
                    'main': forecast_item.get('main', {}),
                    'weather': forecast_item.get('weather', []),
                    'wind': forecast_item.get('wind', {}),
                    'pop': forecast_item.get('pop', 0),
                    'visibility': forecast_item.get('visibility', 0),
                    'clouds': forecast_item.get('clouds', {}),
                    'dt_txt': forecast_item.get('dt_txt', '')
                })

        # Convert hourly forecasts to our format (same as forecast data for OpenWeather)
        hourly_list = []
        for hourly_forecast in forecast_data.get('list', []):
            timestamp = hourly_forecast.get('dt')
            if timestamp:
                hourly_datetime = datetime.fromtimestamp(timestamp)
                hourly_item = {
                    'dt': int(hourly_datetime.timestamp()),
                    'main': hourly_forecast.get('main', {}),
                    'weather': hourly_forecast.get('weather', []),
                    'wind': hourly_forecast.get('wind', {}),
                    'pop': hourly_forecast.get('pop', 0),
                    'visibility': hourly_forecast.get('visibility', 0),
                    'clouds': hourly_forecast.get('clouds', {}),
                    'dt_txt': hourly_forecast.get('dt_txt', '')
                }
                hourly_list.append(hourly_item)

        # Combine all weather data
        weather_data = {
            'current': current_weather,
            'forecast': {'list': forecast_list},
            'hourly': {'hourly': hourly_list, 'note': 'Using OpenWeather API 5-day forecast'},
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
        
        return weather_data, None
        
    except Exception as e:
        return None, str(e)

def get_youtube_videos(location, max_results=3):
    """Get YouTube videos for the location"""
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    if not youtube_api_key:
        return None, "YouTube API key not configured"
    
    try:
        search_query = f"{location} weather travel"
        response = requests.get(
            'https://www.googleapis.com/youtube/v3/search',
            params={
                'part': 'snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': max_results,
                'key': youtube_api_key,
                'order': 'relevance',
                'videoDuration': 'short'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('items', []), None
        elif response.status_code == 403:
            # Try to get more details about the 403 error
            try:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Unknown 403 error')
                return None, f"YouTube API 403 Forbidden: {error_message}"
            except:
                return None, "YouTube API 403 Forbidden: Check API key and quota limits"
        else:
            return None, f"YouTube API error: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "YouTube API request timed out"
    except Exception as e:
        return None, str(e)

def get_google_maps_data(location):
    """Get Google Maps data for the location"""
    if not GOOGLE_MAPS_API_KEY:
        return None, "Google Maps API key not configured"
    
    try:
        # Geocoding API to get coordinates
        geocode_response = requests.get(
            'https://maps.googleapis.com/maps/api/geocode/json',
            params={
                'address': location,
                'key': GOOGLE_MAPS_API_KEY
            }
        )
        
        if geocode_response.status_code == 200:
            geocode_data = geocode_response.json()
            if geocode_data['status'] == 'OK':
                location_data = geocode_data['results'][0]
                return {
                    'formatted_address': location_data['formatted_address'],
                    'geometry': location_data['geometry'],
                    'place_id': location_data['place_id']
                }, None
            else:
                return None, f"Geocoding error: {geocode_data['status']}"
        else:
            return None, f"Google Maps API error: {geocode_response.status_code}"
    except Exception as e:
        return None, str(e)

def get_nearby_places(lat, lon, place_type, max_results=5):
    """Get nearby places using Google Places API - optimized for performance"""
    places_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not places_api_key:
        return None, "Google Places API key not configured"
    
    try:

        
        # Nearby Search API - get more results initially to sort by rating
        nearby_response = requests.get(
            f"{GOOGLE_PLACES_BASE_URL}/nearbysearch/json",
            params={
                'location': f"{lat},{lon}",
                'rankby': 'distance',
                'type': place_type,
                'key': places_api_key
            }
        )
        
        if nearby_response.status_code == 200:
            nearby_data = nearby_response.json()
            if nearby_data['status'] == 'OK':
                places = nearby_data.get('results', [])
        
                
                # Filter places with ratings and sort by number of reviews (highest first)
                rated_places = [p for p in places if p.get('rating') is not None and p.get('user_ratings_total', 0) > 0]
                rated_places.sort(key=lambda x: (x.get('user_ratings_total', 0), x.get('rating', 0)), reverse=True)
                
                # Take top 5 by rating
                top_places = rated_places[:max_results]
        
                
                # Enrich places with additional details (only for top 5)
                enriched_places = []
                for place in top_places:
                    place_id = place.get('place_id')
                    if place_id:
                        # Get place details with minimal fields for faster response
                        details_response = requests.get(
                            f"{GOOGLE_PLACES_BASE_URL}/details/json",
                            params={
                                'place_id': place_id,
                                'fields': 'formatted_address,formatted_phone_number,opening_hours,website,price_level,photos',
                                'key': places_api_key
                            }
                        )
                        
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            if details_data['status'] == 'OK':
                                place_details = details_data['result']
                                # Merge basic info with details
                                enriched_place = {
                                    'place_id': place_id,
                                    'name': place.get('name'),
                                    'formatted_address': place_details.get('formatted_address'),
                                    'formatted_phone_number': place_details.get('formatted_phone_number'),
                                    'website': place_details.get('website'),
                                    'rating': place.get('rating'),
                                    'user_ratings_total': place.get('user_ratings_total'),
                                    'price_level': place_details.get('price_level'),
                                    'opening_hours': place_details.get('opening_hours'),
                                    'photos': place_details.get('photos', []),
                                    'geometry': place.get('geometry'),
                                    'vicinity': place.get('vicinity'),
                                    'types': place.get('types', [])
                                }
                                enriched_places.append(enriched_place)
                            else:
                                # Use basic info if details fail
                                enriched_places.append(place)
                        else:
                            # Use basic info if details request fails
                            enriched_places.append(place)
                
        
                return enriched_places, None
            else:
                return None, f"Nearby search error: {nearby_data['status']}"
        else:
            return None, f"Google Places API error: {nearby_response.status_code}"
    except Exception as e:

        return None, str(e)

def get_place_photo(photo_reference, max_width=400):
    """Get place photo using Google Places Photo API"""
    places_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not places_api_key:
        return None, "Google Places API key not configured"
    
    try:
        photo_url = f"{GOOGLE_PLACES_BASE_URL}/photo"
        params = {
            'maxwidth': max_width,
            'photo_reference': photo_reference,
            'key': places_api_key
        }
        
        # Return the photo URL
        return f"{photo_url}?maxwidth={max_width}&photo_reference={photo_reference}&key={places_api_key}", None
    except Exception as e:
        return None, str(e)

# CRUD Operations

@app.route('/api/weather', methods=['POST'])
def create_weather_record():
    """CREATE - Create a new weather record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([location, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: location, start_date, end_date'}), 400
        
        # Validate date range
        is_valid_date, date_result = validate_date_range(start_date, end_date)
        if not is_valid_date:
            return jsonify({'error': date_result}), 400
        
        start_date_obj, end_date_obj = date_result
        
        # Validate location
        is_valid_location, location_result = validate_location(location)
        if not is_valid_location:
            return jsonify({'error': location_result}), 400
        
        lat, lon = location_result['latitude'], location_result['longitude']
        
        # Get weather data
        weather_data, weather_error = get_weather_data(lat, lon, start_date_obj, end_date_obj)
        if weather_error:
            return jsonify({'error': weather_error}), 500
        
        # Create database record
        new_record = WeatherRecord(
            location=location,
            latitude=lat,
            longitude=lon,
            start_date=start_date_obj,
            end_date=end_date_obj,
            temperature_data=weather_data
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Weather record created successfully',
            'id': new_record.id,
            'data': weather_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather', methods=['GET'])
def read_weather_records():
    """READ - Get all weather records with optional filtering"""
    try:
        # Query parameters for filtering
        location = request.args.get('location')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = WeatherRecord.query
        
        if location:
            query = query.filter(WeatherRecord.location.ilike(f'%{location}%'))
        
        if start_date:
            query = query.filter(WeatherRecord.start_date >= start_date)
        
        if end_date:
            query = query.filter(WeatherRecord.end_date <= end_date)
        
        records = query.order_by(WeatherRecord.created_at.desc()).limit(limit).offset(offset).all()
        
        result = []
        for record in records:
            result.append({
                'id': record.id,
                'location': record.location,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'start_date': record.start_date.isoformat(),
                'end_date': record.end_date.isoformat(),
                'temperature_data': record.temperature_data,
                'created_at': record.created_at.isoformat(),
                'updated_at': record.updated_at.isoformat()
            })
        
        return jsonify({
            'records': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<int:record_id>', methods=['GET'])
def read_weather_record(record_id):
    """READ - Get a specific weather record"""
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        return jsonify({
            'id': record.id,
            'location': record.location,
            'latitude': record.latitude,
            'longitude': record.longitude,
            'start_date': record.start_date.isoformat(),
            'end_date': record.end_date.isoformat(),
            'temperature_data': record.temperature_data,
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<int:record_id>', methods=['PUT'])
def update_weather_record(record_id):
    """UPDATE - Update a weather record"""
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'location' in data:
            location = data['location']
            is_valid_location, location_result = validate_location(location)
            if not is_valid_location:
                return jsonify({'error': location_result}), 400
            
            record.location = location
            record.latitude = location_result['latitude']
            record.longitude = location_result['longitude']
        
        if 'start_date' in data or 'end_date' in data:
            start_date = data.get('start_date', record.start_date.isoformat())
            end_date = data.get('end_date', record.end_date.isoformat())
            
            is_valid_date, date_result = validate_date_range(start_date, end_date)
            if not is_valid_date:
                return jsonify({'error': date_result}), 400
            
            start_date_obj, end_date_obj = date_result
            record.start_date = start_date_obj
            record.end_date = end_date_obj
        
        # Refresh weather data if location or dates changed
        if any(key in data for key in ['location', 'start_date', 'end_date']):
            weather_data, weather_error = get_weather_data(
                record.latitude, 
                record.longitude, 
                record.start_date, 
                record.end_date
            )
            
            if weather_error:
                return jsonify({'error': weather_error}), 500
            
            record.temperature_data = weather_data
        
        record.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Weather record updated successfully',
            'id': record.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/<int:record_id>', methods=['DELETE'])
def delete_weather_record(record_id):
    """DELETE - Delete a weather record"""
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'Weather record deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# API Integration Endpoints

@app.route('/api/youtube/<int:record_id>', methods=['GET'])
def get_location_youtube_videos(record_id):
    """Get YouTube videos for a specific weather record location"""
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        videos, error = get_youtube_videos(record.location)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'location': record.location,
            'videos': videos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/youtube/direct/<location>', methods=['GET'])
def get_youtube_videos_direct(location):
    """Get YouTube videos directly for a location without creating weather records"""
    try:
        # Decode the location from URL
        decoded_location = requests.utils.unquote(location)
        
        videos, error = get_youtube_videos(decoded_location)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'location': decoded_location,
            'videos': videos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maps/<int:record_id>', methods=['GET'])
def get_location_maps_data(record_id):
    """Get Google Maps data for a specific weather record location"""
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        maps_data, error = get_google_maps_data(record.location)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'location': record.location,
            'maps_data': maps_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nearby/<place_type>')
def get_nearby_places_endpoint(place_type):
    """Get nearby places by type (restaurant, hospital, lodging)"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        
        if not lat or not lon:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        if place_type not in ['restaurant', 'hospital', 'lodging']:
            return jsonify({'error': 'Invalid place type. Use: restaurant, hospital, or lodging'}), 400
        
        places, error = get_nearby_places(lat, lon, place_type)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({'places': places or []}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/places/photo')
def get_place_photo_endpoint():
    """Get place photo URL"""
    try:
        photo_reference = request.args.get('photo_reference')
        max_width = request.args.get('max_width', 400, type=int)
        
        if not photo_reference:
            return jsonify({'error': 'Photo reference is required'}), 400
        
        photo_url, error = get_place_photo(photo_reference, max_width)
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({'photo_url': photo_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/places/details/<place_id>')
def get_place_details_endpoint(place_id):
    """Get detailed information about a specific place"""
    try:
        if not GOOGLE_PLACES_API_KEY:
            return jsonify({'error': 'Google Places API key not configured'}), 500
        
        details_response = requests.get(
            f"{GOOGLE_PLACES_BASE_URL}/details/json",
            params={
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,opening_hours,website,price_level,rating,user_ratings_total,photos,geometry',
                'key': GOOGLE_PLACES_API_KEY
            }
        )
        
        if details_response.status_code == 200:
            details_data = details_response.json()
            if details_data['status'] == 'OK':
                return jsonify(details_data['result']), 200
            else:
                return jsonify({'error': f"Place details error: {details_data['status']}"}), 500
        else:
            return jsonify({'error': f"Google Places API error: {details_response.status_code}"}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Data Export Endpoints

@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export weather records as JSON"""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        
        data = []
        for record in records:
            data.append({
                'id': record.id,
                'location': record.location,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'start_date': record.start_date.isoformat(),
                'end_date': record.end_date.isoformat(),
                'temperature_data': record.temperature_data,
                'created_at': record.created_at.isoformat(),
                'updated_at': record.updated_at.isoformat()
            })
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export weather records as CSV"""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Location', 'Latitude', 'Longitude', 'Start Date', 'End Date', 'Created At', 'Updated At'])
        
        # Write data
        for record in records:
            writer.writerow([
                record.id,
                record.location,
                record.latitude,
                record.longitude,
                record.start_date.isoformat(),
                record.end_date.isoformat(),
                record.created_at.isoformat(),
                record.updated_at.isoformat()
            ])
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='weather_records.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/xml', methods=['GET'])
def export_xml():
    """Export weather records as XML"""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        
        root = ET.Element('weather_records')
        
        for record in records:
            record_elem = ET.SubElement(root, 'record')
            
            ET.SubElement(record_elem, 'id').text = str(record.id)
            ET.SubElement(record_elem, 'location').text = record.location
            ET.SubElement(record_elem, 'latitude').text = str(record.latitude)
            ET.SubElement(record_elem, 'longitude').text = str(record.longitude)
            ET.SubElement(record_elem, 'start_date').text = record.start_date.isoformat()
            ET.SubElement(record_elem, 'end_date').text = record.end_date.isoformat()
            ET.SubElement(record_elem, 'created_at').text = record.created_at.isoformat()
            ET.SubElement(record_elem, 'updated_at').text = record.updated_at.isoformat()
        
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        return send_file(
            io.BytesIO(xml_str.encode('utf-8')),
            mimetype='application/xml',
            as_attachment=True,
            download_name='weather_records.xml'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    """Export weather records as PDF"""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title = Paragraph("Weather Records Report", styles['Title'])
        elements.append(title)
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Table data
        data = [['ID', 'Location', 'Start Date', 'End Date', 'Created At']]
        
        for record in records:
            data.append([
                str(record.id),
                record.location,
                record.start_date.strftime('%Y-%m-%d'),
                record.end_date.strftime('%Y-%m-%d'),
                record.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#FFFFFF'),
            ('TEXTCOLOR', (0, 1), (-1, -1), '#000000'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, '#000000')
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='weather_records.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/markdown', methods=['GET'])
def export_markdown():
    """Export weather records as Markdown"""
    try:
        records = WeatherRecord.query.order_by(WeatherRecord.created_at.desc()).all()
        
        markdown_content = "# Weather Records Report\n\n"
        markdown_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += "| ID | Location | Start Date | End Date | Created At |\n"
        markdown_content += "|----|----------|------------|----------|------------|\n"
        
        for record in records:
            markdown_content += f"| {record.id} | {record.location} | {record.start_date.strftime('%Y-%m-%d')} | {record.end_date.strftime('%Y-%m-%d')} | {record.created_at.strftime('%Y-%m-%d %H:%M')} |\n"
        
        return send_file(
            io.BytesIO(markdown_content.encode('utf-8')),
            mimetype='text/markdown',
            as_attachment=True,
            download_name='weather_records.md'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
