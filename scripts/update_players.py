#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.data_service import DataService

def update_market_players():
    """Update market players and their transactions"""
    service = DataService()
    
    try:
        print("🔄 Updating market players...")
        success, message = service.update_market_players()
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Error updating market players: {message}")
            return False
            
        print("🔄 Updating player transactions...")
        success, message = service.update_player_transactions()
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Error updating player transactions: {message}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        service.close()

if __name__ == "__main__":
    print("Starting market player data update...")
    success = update_market_players()
    if success:
        print("✅ All market player data updated successfully!")
    else:
        print("❌ Failed to update market player data!")
        sys.exit(1)