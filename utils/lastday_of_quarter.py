from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import LastDayQuarter, get_session

def last_day_of_month(year, month):
    # The last day of the month is the day before the first day of the next month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day

def generate_quarter_end_dates(start_year, end_year):
    quarter_ends = []
    for year in range(start_year, end_year + 1):
        for quarter in range(1, 5):
            if quarter == 1:
                month = 3
            elif quarter == 2:
                month = 6
            elif quarter == 3:
                month = 9
            else:  # quarter == 4
                month = 12
            last_day = last_day_of_month(year, month)
            date_str = f"{year:04d}{month:02d}{last_day:02d}"
            quarter_ends.append(date_str)
    return quarter_ends

def save_quarter_end_dates_to_db(quarter_end_dates):
    """Save quarter end dates to the lastday_quarter table"""
    session = get_session()
    
    try:
        # Clear existing data
        session.query(LastDayQuarter).delete()
        
        # Insert new data
        for date_str in quarter_end_dates:
            quarter_end = LastDayQuarter(end_date=date_str)
            session.add(quarter_end)
        
        session.commit()
        print(f"Successfully saved {len(quarter_end_dates)} quarter end dates to database")
        
    except Exception as e:
        session.rollback()
        print(f"Error saving quarter end dates: {e}")
        raise
    finally:
        session.close()

def main():
    # Generate the list from 2020 to 2050
    quarter_end_dates = generate_quarter_end_dates(2020, 2050)
    
    # Print the result
    print("Generated quarter end dates:")
    for date in quarter_end_dates:
        print(date)
    
    # Save to database
    save_quarter_end_dates_to_db(quarter_end_dates)

if __name__ == "__main__":
    main()
