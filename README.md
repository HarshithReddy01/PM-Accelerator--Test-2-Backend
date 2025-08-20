# Weather Web App - Backend

**Author**: Harshith Reddy Nalla

A robust Flask-based REST API backend for a comprehensive weather forecasting application. This backend provides weather data, location services, data export capabilities, and integration with external APIs.

## Live Application

**Frontend**: [Weather App Frontend](https://harshithreddy01.github.io/PM-Accelerator--Test-2-Frontend-new/) - Deployed on GitHub Pages (Works everything fine connected to this repo i.e., backend)

**Backend**: Deployed on AWS EC2 with Docker containerization

**Portfolio**: [Personal Website](https://harshithreddy01.github.io/My-Web/) - Showcasing my projects and skills

## Deployment Pipeline

The application follows a complete CI/CD pipeline:

**Local Changes → GitHub Commit → Pipeline → Automatic Docker Compose → EC2 Hosting**

### Pipeline Flow:
1. **Local Development**: Make changes to the codebase
2. **GitHub Commit**: Push changes to GitHub repository
3. **Automated Pipeline**: GitHub Actions triggers deployment
4. **Docker Containerization**: Application is containerized using Docker
5. **EC2 Deployment**: Container is automatically deployed to AWS EC2 instance
6. **Live Application**: Frontend (GitHub Pages) connects to backend (EC2)

### Technologies Used in Deployment:
- **Containerization**: Docker with Docker Compose
- **Cloud Platform**: Ag
- **Frontend Hosting**: GitHub PagesWS EC2 for backend hostin
- **CI/CD**: GitHub Actions for automated deployment
- **Database**: AWS RDS MySQL Database
- **Load Balancer**: AWS Application Load Balancer (if configured)

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
- **Framework**: Flask 2.3.3 (I can also do really good job if I use spring:boot)
- **Database**: SQLAlchemy with MySQL/PostgreSQL support
- **API Documentation**: RESTful API design
- **Authentication**: Environment-based configuration
- **Deployment**: Gunicorn WSGI server
- **Containerization**: Docker with Docker Compose
- **Cloud Infrastructure**: AWS EC2, RDS, Application Load Balancer

### Project Structure
```
backend/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── gunicorn.conf.py      # Production server configuration
├── wsgi.py              # WSGI entry point
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose configuration
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
- Docker and Docker Compose (for containerized deployment)
- API keys for external services:
  - OpenWeatherMap API key
  - Google Places API key
  - YouTube Data API key

## Installation

### Local Development Setup

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

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and database configuration
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode**
   ```bash
   docker-compose up -d
   ```

3. **Stop the containers**
   ```bash
   docker-compose down
   ```

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

### Docker Mode
```bash
docker-compose up
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

## Deployment Architecture

### AWS Infrastructure
- **EC2 Instance**: Hosts the Docker containerized application
- **RDS MySQL**: Database service for data persistence
- **Application Load Balancer**: Distributes traffic and handles SSL termination
- **Security Groups**: Network security configuration
- **VPC**: Virtual private cloud for network isolation

### Docker Configuration
- **Multi-stage build**: Optimized container size
- **Health checks**: Container health monitoring
- **Environment variables**: Secure configuration management
- **Volume mounts**: Persistent data storage

### CI/CD Pipeline
- **GitHub Actions**: Automated deployment workflow
- **Docker Registry**: Container image storage
- **EC2 Deployment**: Automated container deployment
- **Health Monitoring**: Application health verification

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
- Docker security best practices

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

5. **Docker Issues**
   - Check Docker daemon is running
   - Verify Docker Compose version
   - Check container logs: `docker-compose logs`

6. **EC2 Deployment Issues**
   - Verify security group configurations
   - Check instance health status
   - Review CloudWatch logs

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

**Portfolio**: [Personal Website](https://harshithreddy01.github.io/My-Web/) - Showcasing my projects and skills


## Deployment Notes

The application is successfully deployed on AWS EC2 with the following considerations:

- **HTTPS Configuration**: The backend is configured to handle HTTPS requests through the Application Load Balancer
- **Frontend Integration**: The React frontend deployed on GitHub Pages connects seamlessly to the EC2 backend
- **Database**: AWS RDS MySQL provides reliable data persistence
- **Scalability**: Docker containerization allows for easy scaling and deployment
- **Monitoring**: CloudWatch integration for application monitoring and logging

The complete pipeline ensures that any code changes are automatically deployed to production, maintaining a robust and reliable weather application service.

## Special Thanks

Special thanks to **PM Accelerator** for providing this incredible opportunity to showcase my skills and build this comprehensive weather application. This project has been an excellent learning experience in full-stack development, cloud deployment, and modern software engineering practices.
