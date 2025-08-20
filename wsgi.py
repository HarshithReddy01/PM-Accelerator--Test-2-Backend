import os
from dotenv import load_dotenv
from app import app, db

load_dotenv()

if os.getenv("RUN_DB_INIT") == "1":
    with app.app_context():
        db.create_all()

application = app
app = application
