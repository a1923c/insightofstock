#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService

def test_financial_reports():
    """Test financial reports functionality with end_date filter"""
    service = DataService()
    
    try:
        # Test with a specific ticker
        ts_code = "000001.SZ"  # Example ticker, replace with an actual ticker in your database
        print(f"Testing financial reports for {ts_code}")
        
        # Get all financial reports for the ticker
        reports = service.get_financial_reports(ts_code)
        if reports:
            print(f"Found {len(reports['balance_sheets'])} balance sheets")
            print(f"Found {len(reports['cash_flows'])} cash flows")
            print(f"Found {len(reports['income_statements'])} income statements")
            
            if reports['balance_sheets']:
                end_date = reports['balance_sheets'][0]['end_date']
                print(f"\nTesting with end_date filter: {end_date}")
                
                # Get financial reports with end_date filter
                filtered_reports = service.get_financial_reports(ts_code, end_date)
                if filtered_reports:
                    print(f"Found {len(filtered_reports['balance_sheets'])} balance sheets with end_date filter")
                    print(f"Found {len(filtered_reports['cash_flows'])} cash flows with end_date filter")
                    print(f"Found {len(filtered_reports['income_statements'])} income statements with end_date filter")
                    
                    # Verify that all filtered reports have the correct end_date
                    all_correct_date = True
                    for bs in filtered_reports['balance_sheets']:
                        if bs['end_date'] != end_date:
                            all_correct_date = False
                            break
                    for cf in filtered_reports['cash_flows']:
                        if cf['end_date'] != end_date:
                            all_correct_date = False
                            break
                    for is_item in filtered_reports['income_statements']:
                        if is_item['end_date'] != end_date:
                            all_correct_date = False
                            break
                    
                    if all_correct_date:
                        print("✅ All filtered reports have the correct end_date")
                    else:
                        print("❌ Some filtered reports do not have the correct end_date")
                else:
                    print("❌ No filtered reports found")
            else:
                print("❌ No balance sheets found to test end_date filter")
        else:
            print("❌ No financial reports found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        service.close()

if __name__ == "__main__":
    print("Testing financial reports functionality...")
    test_financial_reports()
    print("Test completed!")
