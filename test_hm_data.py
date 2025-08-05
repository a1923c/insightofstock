#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from models import create_tables

def test_hm_data():
    """Test loading hm_list and hm_detail data"""
    # Create tables if they don't exist
    create_tables()
    
    # Initialize data service
    service = DataService()
    
    try:
        print("🔄 Testing hm_list update...")
        success, message = service.update_hm_list()
        if success:
            print(f"✅ hm_list update successful: {message}")
        else:
            print(f"❌ Error updating hm_list: {message}")
            
        print("\n🔄 Testing hm_detail update...")
        success, message = service.update_hm_detail()
        if success:
            print(f"✅ hm_detail update successful: {message}")
        else:
            print(f"❌ Error updating hm_detail: {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting hm data test...")
    test_hm_data()
    print("Test completed!")
