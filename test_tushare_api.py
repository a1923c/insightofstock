#!/usr/bin/env python3
import os
import tushare as ts
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
load_dotenv()

def test_tushare_api():
    """Test Tushare API methods for market players and player transactions"""
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("TUSHARE_TOKEN not found in environment variables")
        return
    
    ts.set_token(token)
    pro = ts.pro_api()
    
    print("Testing hm_list (market players)...")
    try:
        # Test hm_list with minimal parameters
        df = pro.hm_list()
        print(f"hm_list returned {len(df)} rows")
        if not df.empty:
            print("Columns in hm_list response:")
            print(df.columns.tolist())
            print("\nFirst few rows:")
            print(df.head())
        else:
            print("hm_list returned empty DataFrame")
    except Exception as e:
        print(f"Error calling hm_list: {e}")
    
    print("\nTesting hm_detail (player transactions)...")
    try:
        # Test hm_detail with minimal parameters
        df = pro.hm_detail()
        print(f"hm_detail returned {len(df)} rows")
        if not df.empty:
            print("Columns in hm_detail response:")
            print(df.columns.tolist())
            print("\nFirst few rows:")
            print(df.head())
        else:
            print("hm_detail returned empty DataFrame")
    except Exception as e:
        print(f"Error calling hm_detail: {e}")

if __name__ == "__main__":
    test_tushare_api()
