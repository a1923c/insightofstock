#!/usr/bin/env python3
import sys
sys.path.insert(0, '/var/www/insightofstock')
import os
os.chdir('/var/www/insightofstock')

from services.data_service import DataService

def update_data():
    service = DataService()
    try:
        print("Starting data update process...")
        
        # Update tickers
        success, message = service.update_tickers()
        print(f"Tickers update: {message}")
        
        # Update holders
        success, message = service.update_top_holders()
        print(f"Holders update: {message}")
        
        print("Data update completed successfully!")
        
    except Exception as e:
        print(f"Error during data update: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    update_data()