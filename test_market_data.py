#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from models import create_tables

def test_market_data():
    """Test loading market players and player transactions"""
    # Create tables if they don't exist
    create_tables()
    
    # Initialize data service
    service = DataService()
    
    try:
        print("🔄 Testing market players update...")
        success, message = service.update_market_players()
        if success:
            print(f"✅ Market players update successful: {message}")
        else:
            print(f"❌ Error updating market players: {message}")
            
        print("\n🔄 Testing player transactions update...")
        success, message = service.update_player_transactions()
        if success:
            print(f"✅ Player transactions update successful: {message}")
        else:
            print(f"❌ Error updating player transactions: {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting market data test...")
    test_market_data()
    print("Test completed!")
