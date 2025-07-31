from datetime import datetime, timedelta

# Function to get the end date of each quarter
def get_quarter_end_dates(start_year, end_year):
    quarter_end_dates = []
    for year in range(start_year, end_year + 1):
        # Define the end dates for each quarter
        q1_end = datetime(year, 3, 31)
        q2_end = datetime(year, 6, 30)
        q3_end = datetime(year, 9, 30)
        q4_end = datetime(year, 12, 31)
        
        # Append the formatted dates to the list
        quarter_end_dates.extend([
            q1_end.strftime('%Y%m%d'),
            q2_end.strftime('%Y%m%d'),
            q3_end.strftime('%Y%m%d'),
            q4_end.strftime('%Y%m%d')
        ])
    
    return quarter_end_dates

# Generate and print the end dates from 2010 to 2026
end_dates = get_quarter_end_dates(2010, 2026)
for date in end_dates:
    print(date)
