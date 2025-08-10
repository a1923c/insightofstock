#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from models import create_tables

def test_fina_indicators():
    """Test loading financial indicators data"""
    # Create tables if they don't exist
    create_tables()
    
    # Initialize data service
    service = DataService()
    
    try:
        print("🔄 Testing financial indicators update...")
        success, message = service.update_fina_indicators()
        if success:
            print(f"✅ Financial indicators update successful: {message}")
        else:
            print(f"❌ Error updating financial indicators: {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting financial indicators test...")
    test_fina_indicators()
    print("Test completed!")
