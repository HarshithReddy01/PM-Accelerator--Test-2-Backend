from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from io import BytesIO

# Import service classes
from services import WeatherService, ExportService, ExternalAPIService, DatabaseService

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
weather_service = WeatherService()
export_service = ExportService()
external_api_service = ExternalAPIService()
database_service = DatabaseService()

# Create database tables
try:
    database_service.create_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {str(e)}")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_connected = database_service.test_connection()
        
        # Get database info
        db_info = database_service.get_database_info()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'connected': db_connected,
                'info': db_info
            },
            'services': {
                'weather_service': 'initialized',
                'export_service': 'initialized',
                'external_api_service': 'initialized',
                'database_service': 'initialized'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Weather CRUD endpoints
@app.route('/api/weather', methods=['POST'])
def create_weather_record():
    """Create a new weather record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([location, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: location, start_date, end_date'}), 400
        
        # Validate location
        is_valid, location_data, error = weather_service.validate_location(location)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate date range
        is_valid, error = weather_service.validate_date_range(start_date, end_date)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Fetch weather data
        is_valid, weather_data, error = weather_service.fetch_weather_data(
            location_data['latitude'],
            location_data['longitude'],
            start_date,
            end_date
        )
        if not is_valid:
            return jsonify({'error': error}), 500
        
        # Create database session
        db_session = database_service.get_session()
        
        try:
            # Create weather record
            is_valid, record, error = weather_service.create_weather_record(
                db_session,
                location,
                start_date,
                end_date,
                location_data['latitude'],
                location_data['longitude'],
                weather_data
            )
            
            if not is_valid:
                return jsonify({'error': error}), 500
            
            return jsonify({
                'message': 'Weather record created successfully',
                'data': {
                    'id': record.id,
                    'location': record.location,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'created_at': record.created_at.isoformat()
                }
            }), 201
            
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather', methods=['GET'])
def get_all_weather_records():
    """Get all weather records"""
    try:
        db_session = database_service.get_session()
        
        try:
            records = weather_service.get_all_weather_records(db_session)
            
            records_data = []
            for record in records:
                records_data.append({
                    'id': record.id,
                    'location': record.location,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'created_at': record.created_at.isoformat() if record.created_at else None,
                    'updated_at': record.updated_at.isoformat() if record.updated_at else None,
                    'temperature_data': record.temperature_data
                })
            
            return jsonify({
                'records': records_data,
                'total': len(records_data)
            }), 200
            
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['GET'])
def get_weather_record(record_id):
    """Get a specific weather record"""
    try:
        db_session = database_service.get_session()
        
        try:
            record = weather_service.get_weather_record_by_id(db_session, record_id)
            
            if not record:
                return jsonify({'error': 'Weather record not found'}), 404
            
            return jsonify({
                'id': record.id,
                'location': record.location,
                'start_date': record.start_date,
                'end_date': record.end_date,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'created_at': record.created_at.isoformat() if record.created_at else None,
                'updated_at': record.updated_at.isoformat() if record.updated_at else None,
                'temperature_data': record.temperature_data
            }), 200
            
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['PUT'])
def update_weather_record(record_id):
    """Update a weather record"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([location, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: location, start_date, end_date'}), 400
        
        db_session = database_service.get_session()
        
        try:
            is_valid, record, error = weather_service.update_weather_record(
                db_session,
                record_id,
                location,
                start_date,
                end_date
            )
            
            if not is_valid:
                return jsonify({'error': error}), 400 if 'not found' in error else 500
            
            return jsonify({
                'message': 'Weather record updated successfully',
                'data': {
                    'id': record.id,
                    'location': record.location,
                    'start_date': record.start_date,
                    'end_date': record.end_date,
                    'latitude': record.latitude,
                    'longitude': record.longitude,
                    'updated_at': record.updated_at.isoformat()
                }
            }), 200
            
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['DELETE'])
def delete_weather_record(record_id):
    """Delete a weather record"""
    try:
        db_session = database_service.get_session()
        
        try:
            is_valid, error = weather_service.delete_weather_record(db_session, record_id)
            
            if not is_valid:
                return jsonify({'error': error}), 404
            
            return jsonify({'message': 'Weather record deleted successfully'}), 200
            
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Today's weather endpoint
@app.route('/api/today/<location>')
def get_todays_weather(location):
    """Get today's weather with 3-hour intervals"""
    try:
        is_valid, data, error = weather_service.get_todays_weather_3hour(location)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Coordinates endpoint for today's weather
@app.route('/api/today/coordinates')
def get_todays_weather_by_coordinates():
    """Get today's weather by coordinates"""
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        
        if not lat or not lon:
            return jsonify({'error': 'Missing latitude or longitude parameters'}), 400
        
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({'error': 'Invalid latitude or longitude values'}), 400
        
        # Use reverse geocoding to get location name
        is_valid, location_data, error = external_api_service.get_reverse_geocoding(lat, lon)
        
        if is_valid:
            location_name = location_data.get('formatted_address', f"{lat},{lon}")
        else:
            location_name = f"{lat},{lon}"
        
        is_valid, data, error = weather_service.get_todays_weather_3hour(location_name)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Export endpoints
@app.route('/api/export/<format_type>')
def export_data(format_type):
    """Export weather records in various formats"""
    try:
        db_session = database_service.get_session()
        
        try:
            is_valid, data, error = export_service.export_records(db_session, format_type)
            
            if not is_valid:
                return jsonify({'error': error}), 400
            
            # Create file response
            if format_type == 'pdf':
                # PDF is binary data
                buffer = BytesIO(data)
                buffer.seek(0)
                return send_file(
                    buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'weather_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                )
            else:
                # Text-based formats
                buffer = BytesIO(data.encode('utf-8'))
                buffer.seek(0)
                return send_file(
                    buffer,
                    mimetype=_get_mime_type(format_type),
                    as_attachment=True,
                    download_name=f'weather_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format_type}'
                )
                
        finally:
            database_service.close_session(db_session)
            
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

def _get_mime_type(format_type):
    """Get MIME type for export format"""
    mime_types = {
        'json': 'application/json',
        'csv': 'text/csv',
        'xml': 'application/xml',
        'markdown': 'text/markdown'
    }
    return mime_types.get(format_type, 'text/plain')

# External API endpoints
@app.route('/api/youtube/<location>')
def get_youtube_videos(location):
    """Get YouTube videos for a location"""
    try:
        max_results = request.args.get('max_results', 5, type=int)
        
        is_valid, videos, error = external_api_service.get_youtube_videos(location, max_results)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'location': location,
            'videos': videos,
            'total': len(videos)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/places/nearby')
def get_nearby_places():
    """Get nearby places"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 5000, type=int)
        place_type = request.args.get('type', 'restaurant')
        
        if not lat or not lon:
            return jsonify({'error': 'Missing latitude or longitude parameters'}), 400
        
        is_valid, places, error = external_api_service.get_nearby_places(lat, lon, radius, place_type)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'latitude': lat,
            'longitude': lon,
            'radius': radius,
            'place_type': place_type,
            'places': places,
            'total': len(places)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/places/multiple')
def get_multiple_place_types():
    """Get multiple types of nearby places"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        place_types = request.args.get('types', 'restaurant,hospital,lodging').split(',')
        
        if not lat or not lon:
            return jsonify({'error': 'Missing latitude or longitude parameters'}), 400
        
        results = external_api_service.get_multiple_place_types(lat, lon, place_types)
        
        return jsonify({
            'latitude': lat,
            'longitude': lon,
            'place_types': place_types,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/maps/embed')
def get_maps_embed_url():
    """Get Google Maps embed URL"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        zoom = request.args.get('zoom', 12, type=int)
        
        if not lat or not lon:
            return jsonify({'error': 'Missing latitude or longitude parameters'}), 400
        
        embed_url = external_api_service.get_google_maps_embed_url(lat, lon, zoom)
        
        return jsonify({
            'latitude': lat,
            'longitude': lon,
            'zoom': zoom,
            'embed_url': embed_url
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Database management endpoints
@app.route('/api/database/stats')
def get_database_stats():
    """Get database statistics"""
    try:
        stats = database_service.get_database_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/database/cleanup', methods=['POST'])
def cleanup_old_records():
    """Clean up old weather records"""
    try:
        data = request.get_json() or {}
        days_old = data.get('days_old', 30)
        
        deleted_count = database_service.cleanup_old_records(days_old)
        
        return jsonify({
            'message': f'Cleaned up {deleted_count} old records',
            'deleted_count': deleted_count,
            'days_old': days_old
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
