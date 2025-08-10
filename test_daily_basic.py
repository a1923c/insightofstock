#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from models import get_session, DailyBasic

def test_daily_basic():
    """Test loading daily basic data"""
    # Create data service
    service = DataService()
    
    try:
        print("🔄 Testing daily basic data update...")
        

        success, message = service.update_daily_basic()
        if success:
            print(f"✅ Financial daily basic update successful: {message}")
        else:
            print(f"❌ Error updating daily basic : {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting daily basic test...")
    test_result = test_daily_basic()
    print(f"Test result: {'Passed' if test_result else 'Failed'}")
    print("Test completed!")
