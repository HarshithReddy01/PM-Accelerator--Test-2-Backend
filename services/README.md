# Services Architecture

This directory contains the service classes that handle all business logic and external API integrations for the Weather App backend.

## 📁 Service Classes

### **1. WeatherService** (`weather_service.py`)
Handles all weather-related operations including CRUD operations and API calls.

**Key Methods:**
- `validate_location(location)` - Validates and geocodes locations
- `validate_date_range(start_date, end_date)` - Validates date range constraints
- `fetch_weather_data(lat, lon, start_date, end_date)` - Fetches weather data from OpenWeather API
- `create_weather_record(db, location, start_date, end_date, lat, lon, temp_data)` - Creates weather records
- `get_all_weather_records(db)` - Retrieves all weather records
- `update_weather_record(db, record_id, location, start_date, end_date)` - Updates weather records
- `delete_weather_record(db, record_id)` - Deletes weather records
- `get_todays_weather_3hour(location)` - Gets today's weather with 3-hour intervals

### **2. ExportService** (`export_service.py`)
Handles data export operations in various formats.

**Key Methods:**
- `export_to_json(records)` - Exports to JSON format
- `export_to_csv(records)` - Exports to CSV format
- `export_to_xml(records)` - Exports to XML format
- `export_to_pdf(records)` - Exports to PDF format
- `export_to_markdown(records)` - Exports to Markdown format
- `export_records(db, format_type)` - Main export method

### **3. ExternalAPIService** (`external_api_service.py`)
Handles all external API integrations.

**Key Methods:**
- `get_youtube_videos(location, max_results)` - Gets YouTube videos for a location
- `get_google_maps_embed_url(lat, lon, zoom)` - Generates Google Maps embed URLs
- `get_nearby_places(lat, lon, radius, place_type)` - Gets nearby places
- `get_place_details(place_id)` - Gets detailed place information
- `get_multiple_place_types(lat, lon, place_types)` - Gets multiple types of places
- `get_location_suggestions(query, max_results)` - Gets location suggestions
- `get_geocoding_info(address)` - Gets geocoding information
- `get_reverse_geocoding(lat, lon)` - Gets reverse geocoding information

### **4. DatabaseService** (`database_service.py`)
Handles database operations and session management.

**Key Methods:**
- `get_session()` - Gets a new database session
- `close_session(session)` - Closes a database session
- `test_connection()` - Tests database connection
- `get_database_info()` - Gets database information
- `execute_raw_query(query, params)` - Executes raw SQL queries
- `get_database_stats()` - Gets database statistics
- `cleanup_old_records(days_old)` - Cleans up old records

## 🏗️ Architecture Benefits

### **Separation of Concerns**
- Each service has a specific responsibility
- Business logic is separated from API endpoints
- Easy to test individual components

### **Maintainability**
- Code is organized and easy to navigate
- Changes to one service don't affect others
- Clear interfaces between services

### **Reusability**
- Services can be used across different endpoints
- Easy to extend functionality
- Consistent error handling

### **Testability**
- Each service can be unit tested independently
- Mock external dependencies easily
- Clear input/output contracts

## 🔧 Usage Example

```python
from services import WeatherService, DatabaseService

# Initialize services
weather_service = WeatherService()
database_service = DatabaseService()

# Get database session
db_session = database_service.get_session()

try:
    # Use weather service
    is_valid, location_data, error = weather_service.validate_location("London")
    if is_valid:
        records = weather_service.get_all_weather_records(db_session)
        # Process records...
finally:
    database_service.close_session(db_session)
```

## 📋 Error Handling

All service methods return consistent error responses:
- **Success**: `(True, data, None)`
- **Error**: `(False, None, error_message)`

## 🔄 Database Sessions

Always use the DatabaseService to manage sessions:
```python
db_session = database_service.get_session()
try:
    # Use session for database operations
    pass
finally:
    database_service.close_session(db_session)
```

## 🚀 Adding New Services

To add a new service:

1. Create a new Python file in the `services/` directory
2. Define your service class with clear methods
3. Add proper error handling and return consistent responses
4. Update `__init__.py` to export the new service
5. Import and use in `app.py`

## 📝 Best Practices

- Keep services focused on a single responsibility
- Use consistent error handling patterns
- Document all public methods
- Handle database sessions properly
- Use type hints for better code clarity
- Test each service independently
