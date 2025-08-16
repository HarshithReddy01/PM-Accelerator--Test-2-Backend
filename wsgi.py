import os
from dotenv import load_dotenv
from app import app, db

# Load environment variables
load_dotenv()
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
