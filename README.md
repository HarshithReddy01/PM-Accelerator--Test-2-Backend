# Weather Web App - Backend

A robust Flask-based REST API backend for a comprehensive weather forecasting application. This backend provides weather data, location services, data export capabilities, and integration with external APIs.

## Features

### Core Weather Functionality
- Real-time weather data retrieval using OpenWeatherMap API
- Current weather conditions and forecasts
- Hourly weather forecasts for specific dates
- Historical weather data storage and retrieval
- Location validation and geocoding services

### Data Management
- Complete CRUD operations for weather records
- Database persistence with SQLAlchemy
- Bulk operations (clear all records)
- Data validation and error handling
-Data

### Export Capabilities
- Multiple export formats: JSON, CSV, XML, PDF, Markdown
- Customizable export options
- File download functionality

### External API Integrations
- YouTube video search for location-based content
- Google Places API for nearby places discovery
- Google Maps integration for location services
- Reverse geocoding services

### Advanced Features
- Health check endpoints for monitoring
- CORS configuration for cross-origin requests
- Security headers implementation
- Comprehensive error handling and logging

## Architecture

### Technology Stack
- **Framework**: Flask 2.3.3
- **Database**: SQLAlchemy with MySQL/PostgreSQL support
- **API Documentation**: RESTful API design
- **Authentication**: Environment-based configuration
- **Deployment**: Gunicorn WSGI server

### Project Structure
```
backend/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── gunicorn.conf.py      # Production server configuration
├── wsgi.py              # WSGI entry point
└── services/
    ├── __init__.py
    ├── database_service.py
    ├── export_service.py
    ├── external_api_service.py
    └── weather_service.py
```

### Database Schema
- **WeatherRecord**: Stores weather data with location, dates, and temperature information
- **Fields**: id, location, latitude, longitude, start_date, end_date, temperature_data, created_at, updated_at

### Database connected to RDS MySQL Database in AWS.

## Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- MySQL or PostgreSQL database
- API keys for external services:
  - OpenWeatherMap API key
  - Google Places API key
  - YouTube Data API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
Clone -> Install python -> Install Dependencies -> python app.py (Terminal)

Also clone the frontend (Backend and frontend should run simultaneously, as I showed in my video)

Install React -> Clone -> Install Dependencies -> Start the server (npm start) -> Results

## Running the Application

### Development Mode
```bash
python app.py
```
The server will start on `http://localhost:5000`

### Production Mode
```bash
gunicorn -c gunicorn.conf.py wsgi:app
```

## API Endpoints

### Health Check
- `GET /api/health` - Application health status

### Weather Records
- `POST /api/weather` - Create new weather record
- `GET /api/weather` - Get all weather records
- `GET /api/weather/<id>` - Get specific weather record
- `PUT /api/weather/<id>` - Update weather record
- `DELETE /api/weather/<id>` - Delete weather record
- `DELETE /api/weather/clear-all` - Clear all records

### Current Weather
- `GET /api/today/<location>` - Get today's weather for location
- `GET /api/today/coordinates` - Get weather by coordinates

### Hourly Forecast
- `GET /api/hourly/<record_id>` - Get hourly forecast by record
- `GET /api/hourly/direct` - Get hourly forecast by coordinates

### Data Export
- `GET /api/export/json` - Export data as JSON
- `GET /api/export/csv` - Export data as CSV
- `GET /api/export/xml` - Export data as XML
- `GET /api/export/pdf` - Export data as PDF
- `GET /api/export/markdown` - Export data as Markdown

### External Services
- `GET /api/youtube/<location>` - Get YouTube videos for location
- `GET /api/places/nearby` - Get nearby places
- `GET /api/places/multiple` - Get multiple place types
- `GET /api/places/photo` - Get place photos
- `GET /api/maps/embed` - Get Google Maps embed URL

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Database connection string | Yes |
| `OPENWEATHER_API_KEY` | OpenWeatherMap API key | Yes |
| `GOOGLE_PLACES_API_KEY` | Google Places API key | No |
| `YOUTUBE_API_KEY` | YouTube Data API key | No |
| `CORS_ORIGINS` | Allowed CORS origins | No |

## Error Handling

The application implements comprehensive error handling:
- Input validation for all endpoints
- Database error handling with rollback
- External API error handling
- Proper HTTP status codes
- Detailed error messages

## Security Features

- CORS configuration for cross-origin requests
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Input sanitization and validation
- Environment-based configuration

## Testing

To test the API endpoints:

1. Start the server
2. Use tools like Postman or curl to test endpoints
3. Example curl command:
   ```bash
   curl -X GET http://localhost:5000/api/health
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify DATABASE_URL in .env file
   - Ensure database server is running
   - Check database credentials

2. **API Key Issues**
   - Verify API keys are correctly set in .env
   - Check API key permissions and quotas

3. **CORS Errors**
   - Update CORS_ORIGINS in .env file
   - Ensure frontend URL is included

4. **Port Already in Use**
   - Change port in app.py or gunicorn.conf.py
   - Kill existing processes using the port

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact harshithreddy0117@gmail.com

I wanted to let you know that I did manage to deploy my weather backend to AWS, but after deployment I ran into an issue. The backend itself runs fine, I can see the responses in the console, but the problem is that EC2 blocks the API calls because they are served over HTTP while EC2 expects HTTPS. Because of that, the frontend cannot pull the data even though the backend is working.

Before deployment I should have taken care of configuring HTTPS (by attaching a custom domain and SSL certificate), but that requires purchasing a domain and setting up additional permissions, which I didn’t have the time to complete within the given deadline. I actually went a step further and integrated Docker, created an image, and hosted the container on EC2 successfully. So the service is technically running, just not accessible from the frontend due to the HTTP/HTTPS mismatch.

Since the deadline is close, I decided to remove the Docker/EC2 setup for the submission and run the backend locally instead. This way, you can clone the repository and test it on your machine without worrying about HTTPS or EC2 restrictions. The local version works smoothly and demonstrates all the required functionality.

I want to thank you again for the opportunity. I know I went beyond the basic requirements by trying Docker + AWS deployment, and even though it didn’t fully work out on EC2 due to the HTTPS issue, the local version shows the complete implementation.
