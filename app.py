from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from io import BytesIO
from models import db, WeatherRecord
from services import WeatherService, ExportService, ExternalAPIService

#Im getting .env
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
db.init_app(app)
weather_service = WeatherService()
export_service = ExportService()
external_api_service = ExternalAPIService()
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db_connected = True
        try:
            db.session.execute("SELECT 1")
        except:
            db_connected = False
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'connected': db_connected,
                'info': 'Flask-SQLAlchemy initialized'
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

@app.route('/api/weather', methods=['POST'])
def create_weather_record():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([location, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: location, start_date, end_date'}), 400
        
        is_valid, location_data, error = weather_service.validate_location(location)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        is_valid, error = weather_service.validate_date_range(start_date, end_date)
        if not is_valid:
            return jsonify({'error': error}), 400
        
        is_valid, weather_data, error = weather_service.fetch_weather_data(
            location_data['latitude'],
            location_data['longitude'],
            start_date,
            end_date
        )
        if not is_valid:
            return jsonify({'error': error}), 500
        
        try:
            weather_record = WeatherRecord(
                location=location,
                start_date=start_date,
                end_date=end_date,
                latitude=location_data['latitude'],
                longitude=location_data['longitude'],
                temperature_data=weather_data
            )
            
            db.session.add(weather_record)
            db.session.commit()
            db.session.refresh(weather_record)
            
            return jsonify({
                'message': 'Weather record created successfully',
                'data': {
                    'id': weather_record.id,
                    'location': weather_record.location,
                    'start_date': weather_record.start_date,
                    'end_date': weather_record.end_date,
                    'latitude': weather_record.latitude,
                    'longitude': weather_record.longitude,
                    'created_at': weather_record.created_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather', methods=['GET'])
def get_all_weather_records():
    try:
        records = WeatherRecord.query.all()
        
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
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['GET'])
def get_weather_record(record_id):
    try:
        record = WeatherRecord.query.get(record_id)
        
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
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['PUT'])
def update_weather_record(record_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        location = data.get('location')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not all([location, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: location, start_date, end_date'}), 400
        
        record = WeatherRecord.query.get(record_id)
        if not record:
            return jsonify({'error': 'Weather record not found'}), 404
        
        try:
            is_valid, location_data, error = weather_service.validate_location(location)
            if not is_valid:
                return jsonify({'error': error}), 400
            
            is_valid, error = weather_service.validate_date_range(start_date, end_date)
            if not is_valid:
                return jsonify({'error': error}), 400
            
            is_valid, weather_data, error = weather_service.fetch_weather_data(
                location_data['latitude'],
                location_data['longitude'],
                start_date,
                end_date
            )
            if not is_valid:
                return jsonify({'error': error}), 500
            
            record.location = location
            record.start_date = start_date
            record.end_date = end_date
            record.latitude = location_data['latitude']
            record.longitude = location_data['longitude']
            record.temperature_data = weather_data
            record.updated_at = datetime.utcnow()
            
            db.session.commit()
            
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
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Update error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/<int:record_id>', methods=['DELETE'])
def delete_weather_record(record_id):
    try:
        record = WeatherRecord.query.get(record_id)
        
        if not record:
            return jsonify({'error': 'Weather record not found'}), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': 'Weather record deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/weather/clear-all', methods=['DELETE'])
def clear_all_weather_records():
    try:
        record_count = WeatherRecord.query.count()
        
        if record_count == 0:
            return jsonify({'message': 'No weather records to delete'}), 200
        
        WeatherRecord.query.delete()
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {record_count} weather records',
            'deleted_count': record_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/today/<location>')
def get_todays_weather(location):
    try:
        is_valid, data, error = weather_service.get_todays_weather_3hour(location)
        
        if not is_valid:
            return jsonify({'error': error}), 400
        
        return jsonify(data), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/today/coordinates')
def get_todays_weather_by_coordinates():
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

@app.route('/api/export/<format_type>')
def export_data(format_type):
    try:
        records = WeatherRecord.query.all()
        
        if format_type == 'json':
            data = export_service.export_to_json(records)
        elif format_type == 'csv':
            data = export_service.export_to_csv(records)
        elif format_type == 'xml':
            data = export_service.export_to_xml(records)
        elif format_type == 'pdf':
            data = export_service.export_to_pdf(records)
        elif format_type == 'markdown':
            data = export_service.export_to_markdown(records)
        else:
            return jsonify({'error': f'Unsupported export format: {format_type}'}), 400
        
        if format_type == 'pdf':
            buffer = BytesIO(data)
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'weather_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
        else:
            buffer = BytesIO(data.encode('utf-8'))
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype=_get_mime_type(format_type),
                as_attachment=True,
                download_name=f'weather_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format_type}'
            )
            
    except Exception as e:
        return jsonify({'error': f'Export error: {str(e)}'}), 500

def _get_mime_type(format_type):
    mime_types = {
        'json': 'application/json',
        'csv': 'text/csv',
        'xml': 'application/xml',
        'markdown': 'text/markdown'
    }
    return mime_types.get(format_type, 'text/plain')

@app.route('/api/youtube/<location>')
def get_youtube_videos(location):
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

@app.route('/api/places/photo')
def get_place_photo():
    try:
        photo_reference = request.args.get('photo_reference')
        max_width = request.args.get('max_width', 400, type=int)
        
        if not photo_reference:
            return jsonify({'error': 'Missing photo_reference parameter'}), 400
        
        if photo_reference.startswith('mock_photo_'):
            photo_number = photo_reference.split('_')[-1]
            placeholder_url = f'https://via.placeholder.com/{max_width}x300/4A90E2/ffffff?text=Place+Photo+{photo_number}'
            return jsonify({'photo_url': placeholder_url}), 200
        
        if external_api_service.google_places_api_key:
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={external_api_service.google_places_api_key}"
            return jsonify({'photo_url': photo_url}), 200
        else:
            placeholder_url = f'https://via.placeholder.com/{max_width}x300/4A90E2/ffffff?text=Photo+Not+Available'
            return jsonify({'photo_url': placeholder_url}), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/maps/embed')
def get_maps_embed_url():
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



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
