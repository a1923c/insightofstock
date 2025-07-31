"""
Utility functions for date calculations
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_latest_quarter_end_date(date_str=None):
    """
    Get the latest quarter end date before or equal to the given date.
    
    Args:
        date_str (str, optional): Date in format YYYYMMDD. If None, uses current date.
        
    Returns:
        str: Latest quarter end date in format YYYYMMDD
    """
    if date_str:
        date = datetime.strptime(date_str, '%Y%m%d')
    else:
        date = datetime.now()
    
    # Get the quarter (1, 2, 3, or 4)
    quarter = (date.month - 1) // 3 + 1
    
    # Calculate the end date of the current quarter
    quarter_end_month = quarter * 3
    quarter_end_date = datetime(date.year, quarter_end_month, 1) + relativedelta(months=1) - timedelta(days=1)
    
    # If the quarter end date is after the given date, go back to previous quarter
    if quarter_end_date > date:
        quarter_end_date = quarter_end_date - relativedelta(months=3)
    
    return quarter_end_date.strftime('%Y%m%d')

def get_quarter_end_dates(count=4):
    """
    Get a list of the last 'count' quarter end dates.
    
    Args:
        count (int): Number of quarter end dates to return
        
    Returns:
        list: List of quarter end dates in format YYYYMMDD
    """
    dates = []
    current_date = datetime.now()
    
    for i in range(count):
        # Get the quarter for the current date
        quarter = (current_date.month - 1) // 3 + 1
        quarter_end_month = quarter * 3
        quarter_end_date = datetime(current_date.year, quarter_end_month, 1) + relativedelta(months=1) - timedelta(days=1)
        
        # If the quarter end date is after the current date, go back to previous quarter
        if quarter_end_date > current_date:
            quarter_end_date = quarter_end_date - relativedelta(months=3)
            
        dates.append(quarter_end_date.strftime('%Y%m%d'))
        
        # Move to the previous quarter for the next iteration
        current_date = quarter_end_date - timedelta(days=1)
    
    return dates

if __name__ == "__main__":
    # Test the functions
    print(f"Latest quarter end date: {get_latest_quarter_end_date()}")
    print(f"Latest quarter end date (20250801): {get_latest_quarter_end_date('20250801')}")
    print(f"Last 4 quarter end dates: {get_quarter_end_dates(4)}")