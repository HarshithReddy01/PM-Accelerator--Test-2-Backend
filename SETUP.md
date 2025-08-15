# Environment Variables Setup

## Required API Keys

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=sqlite:///weather_app.db

# OpenWeather API Key (Required)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Google Maps Platform API Keys (Optional - for nearby places and maps features)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# YouTube API Key (Optional - for location videos)
YOUTUBE_API_KEY=your_youtube_api_key_here
```

## How to Get API Keys

### OpenWeather API Key (Required)
1. Go to https://openweathermap.org/
2. Sign up for a free account
3. Go to "My API Keys" section
4. Copy your API key

### Google Maps API Keys (Optional)
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API
4. Create credentials (API keys) for each service

### YouTube API Key (Optional)
1. Go to https://console.cloud.google.com/
2. Enable YouTube Data API v3
3. Create credentials (API key)

## Security Notes
- Never commit your `.env` file to version control
- Keep your API keys secure and private
- Use environment variables in production deployments
