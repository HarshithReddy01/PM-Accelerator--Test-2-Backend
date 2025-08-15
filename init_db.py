import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the MySQL database"""
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host='weather-app.cra2qkmiw4fu.ap-south-1.rds.amazonaws.com',
            user='admin',
            password=os.getenv('DB_PASSWORD'),
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS weather_db")
        print("Database 'weather_db' created or already exists")
        
        # Use the database
        cursor.execute("USE weather_db")
        
        # Create weather_records table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS weather_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            location VARCHAR(255) NOT NULL,
            latitude FLOAT,
            longitude FLOAT,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            temperature_data JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_location (location),
            INDEX idx_dates (start_date, end_date),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        print("Table 'weather_records' created or already exists")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database()
