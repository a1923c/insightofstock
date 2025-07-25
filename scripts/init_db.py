#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import create_tables, get_session

def initialize_database():
    """Initialize the database with required tables"""
    try:
        engine = create_tables()
        print("✅ Database tables created successfully!")
        
        # Test database connection
        session = get_session()
        from sqlalchemy import text
        session.execute(text("SELECT 1"))
        print("✅ Database connection test successful!")
        session.close()
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    initialize_database()