@echo off
REM Production startup script for Weather App Backend (Windows)

echo Starting Weather App Backend in production mode...

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Make sure environment variables are set.
)

REM Initialize database
echo Initializing database...
python init_db.py

REM Start Gunicorn server
echo Starting Gunicorn server...
gunicorn --config gunicorn.conf.py wsgi:app

pause
