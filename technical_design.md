# Technical Design Document - Insight of Stock

## Overview
A web application that displays stock tickers with their top 10 shareholders information, allowing users to view detailed holder information by clicking on ticker names.

## Architecture
- **Backend**: Python Flask REST API
- **Database**: SQLite (lightweight, suitable for this use case)
- **Frontend**: HTML/CSS/JavaScript with Bootstrap for responsive design
- **Data Source**: Tushare API for Chinese stock market data
- **Scheduler**: Cron job for daily data updates at 8:00 AM

## Database Schema

### 1. tickers Table
- `id` (INTEGER, PRIMARY KEY)
- `ts_code` (TEXT, UNIQUE) - Tushare stock code
- `symbol` (TEXT) - Stock symbol
- `name` (TEXT) - Company name
- `area` (TEXT) - Geographic area
- `industry` (TEXT) - Industry classification
- `list_date` (TEXT) - Listing date
- `updated_date` (TEXT) - Last update timestamp

### 2. top_holders Table
- `id` (INTEGER, PRIMARY KEY)
- `ts_code` (TEXT, FOREIGN KEY) - Stock code
- `ann_date` (TEXT) - Announcement date
- `end_date` (TEXT) - Reporting period end date
- `holder_name` (TEXT) - Shareholder name
- `hold_amount` (REAL) - Number of shares held
- `hold_ratio` (REAL) - Percentage of shares held
- `updated_date` (TEXT) - Last update timestamp

## API Endpoints

### 1. GET /api/tickers
Returns all tickers with basic information

### 2. GET /api/tickers/<ts_code>/holders
Returns top 10 holders for a specific ticker

### 3. GET /api/update-data
Manual trigger for data update (admin endpoint)

## Frontend Pages

### 1. Home Page (/)
- Table displaying all tickers with:
  - Ticker name/symbol
  - Top holder count
  - Last updated date
- Clickable ticker names to view holder details

### 2. Ticker Detail Page (/ticker/<ts_code>)
- Detailed information about the selected ticker
- Table of top 10 shareholders showing:
  - Holder name
  - Shares held
  - Percentage of total shares
  - Announcement date

## Data Flow
1. **Daily Update**: Cron job triggers data update at 8:00 AM
2. **Data Fetching**: Python script connects to Tushare API
3. **Data Processing**: Parse and transform API responses
4. **Database Update**: Insert/update records in SQLite
5. **Frontend Display**: Users view updated data via web interface

## Security Considerations
- Tushare API token stored in .env file (not committed to git)
- Input validation for API endpoints
- No sensitive data exposure
- Rate limiting consideration for API calls

## Project Structure
```
insightofstock/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── services/             # Business logic
│   ├── tushare_service.py    # Tushare API integration
│   └── data_service.py       # Data processing
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── ticker_detail.html
├── static/               # CSS, JS, images
│   ├── css/
│   └── js/
├── database/             # Database files
│   └── insightofstock.db
├── scripts/              # Utility scripts
│   └── update_data.py   # Data update script
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (gitignored)
└── technical_design.md   # This document
```