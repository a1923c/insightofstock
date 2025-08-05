#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from models import create_tables

def test_financial_statements():
    """Test updating balance sheets, cash flows, and income statements"""
    # Create tables if they don't exist
    create_tables()
    
    # Initialize data service
    service = DataService()
    
    try:
        print("🔄 Testing balance sheets update...")
        success, message = service.update_balance_sheets()
        if success:
            print(f"✅ Balance sheets update successful: {message}")
        else:
            print(f"❌ Error updating balance sheets: {message}")
            
        print("\n🔄 Testing cash flows update...")
        success, message = service.update_cash_flows()
        if success:
            print(f"✅ Cash flows update successful: {message}")
        else:
            print(f"❌ Error updating cash flows: {message}")
            
        print("\n🔄 Testing income statements update...")
        success, message = service.update_income_statements()
        if success:
            print(f"✅ Income statements update successful: {message}")
        else:
            print(f"❌ Error updating income statements: {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting financial statements update test...")
    test_financial_statements()
    print("Test completed!")
