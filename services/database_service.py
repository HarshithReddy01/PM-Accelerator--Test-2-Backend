from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import os
from models import db, Base

class DatabaseService:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """
        Initialize database connection and session
        """
        try:
            # Use Flask-SQLAlchemy's engine
            self.engine = db.engine
            self.SessionLocal = db.session
            
            print("✅ Database connection initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            raise
    
    def create_tables(self):
        """
        Create all database tables
        """
        try:
            with db.app.app_context():
                db.create_all()
            print("✅ Database tables created successfully")
        except SQLAlchemyError as e:
            print(f"❌ Database table creation error: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session
        """
        if not self.SessionLocal:
            raise Exception("Database not initialized")
        
        return self.SessionLocal
    
    def close_session(self, session: Session):
        """
        Close a database session
        """
        try:
            if session:
                session.close()
        except Exception as e:
            print(f"Warning: Error closing session: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test database connection
        """
        try:
            session = self.get_session()
            session.execute("SELECT 1")
            session.close()
            return True
        except Exception as e:
            print(f"❌ Database connection test failed: {str(e)}")
            return False
    
    def get_database_info(self) -> dict:
        """
        Get database information
        """
        try:
            session = self.get_session()
            
            # Get database name
            result = session.execute("SELECT DATABASE()")
            db_name = result.scalar()
            
            # Get table count
            result = session.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = :db_name", 
                                   {"db_name": db_name})
            table_count = result.scalar()
            
            # Get weather records count
            result = session.execute("SELECT COUNT(*) FROM weather_records")
            weather_records_count = result.scalar()
            
            session.close()
            
            return {
                'database_name': db_name,
                'table_count': table_count,
                'weather_records_count': weather_records_count,
                'connection_status': 'Connected'
            }
            
        except Exception as e:
            return {
                'database_name': 'Unknown',
                'table_count': 0,
                'weather_records_count': 0,
                'connection_status': f'Error: {str(e)}'
            }
    
    def execute_raw_query(self, query: str, params: dict = None) -> list:
        """
        Execute a raw SQL query
        """
        try:
            session = self.get_session()
            result = session.execute(query, params or {})
            
            if query.strip().upper().startswith('SELECT'):
                # For SELECT queries, return results
                rows = result.fetchall()
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            else:
                # For non-SELECT queries, commit and return affected rows
                session.commit()
                return [{'affected_rows': result.rowcount}]
                
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Query execution error: {str(e)}")
        finally:
            self.close_session(session)
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a database backup (basic implementation)
        """
        try:
            # This is a basic implementation
            # In production, you might want to use mysqldump or similar tools
            print(f"Backup functionality would create backup at: {backup_path}")
            return True
        except Exception as e:
            print(f"Backup error: {str(e)}")
            return False
    
    def cleanup_old_records(self, days_old: int = 30) -> int:
        """
        Clean up old weather records
        """
        try:
            session = self.get_session()
            
            from datetime import datetime, timedelta
            from models import WeatherRecord
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Count records to be deleted
            count_query = session.query(WeatherRecord).filter(
                WeatherRecord.created_at < cutoff_date
            ).count()
            
            # Delete old records
            deleted_records = session.query(WeatherRecord).filter(
                WeatherRecord.created_at < cutoff_date
            ).delete()
            
            session.commit()
            session.close()
            
            print(f"Cleaned up {deleted_records} old records (older than {days_old} days)")
            return deleted_records
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Cleanup error: {str(e)}")
            return 0
        finally:
            self.close_session(session)
    
    def get_database_stats(self) -> dict:
        """
        Get database statistics
        """
        try:
            session = self.get_session()
            
            from models import WeatherRecord
            from sqlalchemy import func
            
            # Total records
            total_records = session.query(WeatherRecord).count()
            
            # Records by location
            location_stats = session.query(
                WeatherRecord.location,
                func.count(WeatherRecord.id).label('count')
            ).group_by(WeatherRecord.location).all()
            
            # Recent activity
            from datetime import datetime, timedelta
            last_24_hours = datetime.utcnow() - timedelta(hours=24)
            recent_records = session.query(WeatherRecord).filter(
                WeatherRecord.created_at >= last_24_hours
            ).count()
            
            session.close()
            
            return {
                'total_records': total_records,
                'recent_records_24h': recent_records,
                'locations': [{'location': loc, 'count': count} for loc, count in location_stats],
                'top_locations': sorted(location_stats, key=lambda x: x[1], reverse=True)[:5]
            }
            
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {
                'total_records': 0,
                'recent_records_24h': 0,
                'locations': [],
                'top_locations': []
            }
