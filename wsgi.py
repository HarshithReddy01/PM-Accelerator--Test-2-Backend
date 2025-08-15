"""
WSGI entry point for production deployment
"""
import os
from dotenv import load_dotenv
from app import app, db

# Load environment variables
load_dotenv()

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
