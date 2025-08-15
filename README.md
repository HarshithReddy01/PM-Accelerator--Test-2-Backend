# Weather App Backend

A comprehensive Flask backend for the weather application with CRUD operations, API integrations, and data export functionality.

## Features

### 2.1 CRUD Operations (Mandatory)
- **CREATE**: Add weather records with location and date range validation
- **READ**: Retrieve weather records with filtering and pagination
- **UPDATE**: Modify existing weather records with validation
- **DELETE**: Remove weather records from the database

### 2.2 API Integration (Optional)
- **YouTube Videos**: Get location-related videos
- **Google Maps Data**: Retrieve location information and coordinates
- **Location Validation**: Fuzzy matching and geocoding support

### 2.3 Data Export (Optional)
- **JSON Export**: Structured data export
- **CSV Export**: Comma-separated values format
- **XML Export**: XML format with proper structure
- **PDF Export**: Professional PDF reports
- **Markdown Export**: Markdown table format

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the backend directory with your API keys:
```env
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name

# Google Maps Platform API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key

# YouTube API Key
YOUTUBE_API_KEY=your_youtube_api_key

# OpenWeather API Key
OPENWEATHER_API_KEY=ec784b133d32aafc9a94a859ab777fa5
```

**⚠️ SECURITY IMPORTANT:**
- Never commit `.env` files to version control
- Add `.env` to your `.gitignore` file
- Use environment variables in production deployments
- Restrict API keys by HTTP referrer and usage limits

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Run the Application

#### Development Mode
```bash
python app.py
```

#### Production Mode
```bash
# Linux/Mac
chmod +x start_production.sh
./start_production.sh

# Windows
start_production.bat

# Or manually with Gunicorn
gunicorn --config gunicorn.conf.py wsgi:app
```

The server will start on `http://localhost:5000`

## API Endpoints

### CRUD Operations

#### CREATE - Create Weather Record
```
POST /api/weather
Content-Type: application/json

{
  "location": "New York, NY",
  "start_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

#### READ - Get All Weather Records
```
GET /api/weather
GET /api/weather?location=New York&start_date=2024-01-01&limit=10&offset=0
```

#### READ - Get Specific Weather Record
```
GET /api/weather/{record_id}
```

#### UPDATE - Update Weather Record
```
PUT /api/weather/{record_id}
Content-Type: application/json

{
  "location": "Updated Location",
  "start_date": "2024-01-02",
  "end_date": "2024-01-08"
}
```

#### DELETE - Delete Weather Record
```
DELETE /api/weather/{record_id}
```

### API Integration

#### YouTube Videos
```
GET /api/youtube/{record_id}
```

#### Google Maps Data
```
GET /api/maps/{record_id}
```

### Data Export

#### JSON Export
```
GET /api/export/json
```

#### CSV Export
```
GET /api/export/csv
```

#### XML Export
```
GET /api/export/xml
```

#### PDF Export
```
GET /api/export/pdf
```

#### Markdown Export
```
GET /api/export/markdown
```

### Health Check
```
GET /api/health
```

## Database Schema

### weather_records Table
- `id` (INT, Primary Key): Unique identifier
- `location` (VARCHAR(255)): Location name
- `latitude` (FLOAT): Latitude coordinate
- `longitude` (FLOAT): Longitude coordinate
- `start_date` (DATE): Start date for weather data
- `end_date` (DATE): End date for weather data
- `temperature_data` (JSON): Weather data from API
- `created_at` (DATETIME): Record creation timestamp
- `updated_at` (DATETIME): Record update timestamp

## Validation Rules

### Date Range Validation
- Start date cannot be after end date
- Start date cannot be more than 1 year in the past
- End date cannot be more than 7 days in the future
- Date format must be YYYY-MM-DD

### Location Validation
- Location must be geocodable
- Fuzzy matching supported for location names
- Coordinates are automatically retrieved and stored

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include descriptive messages:
```json
{
  "error": "Start date cannot be after end date"
}
```

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SQLAlchemy**: Database ORM
- **PyMySQL**: MySQL database connector
- **requests**: HTTP library for API calls
- **geopy**: Geocoding library
- **pandas**: Data manipulation
- **reportlab**: PDF generation
- **markdown**: Markdown processing
- **gunicorn**: Production WSGI server

## Security Features

- Input validation for all user inputs
- SQL injection prevention through ORM
- CORS configuration for frontend integration
- Environment variable management for API keys

## Performance Features

- Database connection pooling
- Indexed database queries
- Pagination for large datasets
- Efficient JSON storage for weather data
- Multi-worker process support
- Request timeout handling
- Memory leak prevention
- Production-ready logging

## Production Deployment

### WSGI Server Configuration

The application is configured to run with **Gunicorn** as the WSGI server for production deployment.

#### Key Production Features:

- **Multi-worker processes**: Automatically scales based on CPU cores
- **Request limits**: Prevents memory leaks and DoS attacks
- **Timeout handling**: 30-second request timeout
- **Logging**: Structured access and error logging
- **Security**: Request size limits and field validation

#### Deployment Options:

1. **Direct Gunicorn**:
   ```bash
   gunicorn --config gunicorn.conf.py wsgi:app
   ```

2. **Using startup scripts**:
   ```bash
   # Linux/Mac
   ./start_production.sh
   
   # Windows
   start_production.bat
   ```

3. **Behind a reverse proxy** (recommended):
   - Nginx
   - Apache
   - Cloud load balancers

#### Environment Variables for Production:

```env
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# API Keys
GOOGLE_MAPS_API_KEY=your_key
GOOGLE_WEATHER_API_KEY=your_key
GOOGLE_PLACES_API_KEY=your_key
YOUTUBE_API_KEY=your_key
```

#### Monitoring and Logs:

- Access logs: Standard output
- Error logs: Standard error
- Health check endpoint: `/api/health`
- Process management: PID file at `/tmp/gunicorn.pid`
