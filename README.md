# Insight of Stock

A web application that displays Chinese stock **individual shareholders** (自然人) with their holdings across multiple tickers, allowing users to drill down from shareholders to detailed ticker information.

## Features

- **Shareholder Focus**: View individual shareholders and their portfolio holdings
- **Portfolio Analysis**: See how many tickers each shareholder owns
- **Drill-down Capability**: Click on any shareholder to view detailed holdings
- **Real-time Data**: Fetches data from Tushare API
- **Daily Updates**: Automated cron job updates data at 8:00 AM
- **Detailed Holdings**: View shares held, percentage, and changes for each ticker
- **Responsive Design**: Works on desktop and mobile devices

## New Features

### 🆕 Individual Shareholders View
- **Home Page** now shows individual shareholders (自然人) instead of all tickers
- **Ticker Count**: Displays how many different tickers each shareholder owns
- **Drill-down**: Click "View Details" to see all holdings for a specific shareholder

### 🆕 Enhanced Holder Details
- **Portfolio Overview**: Complete list of all tickers owned by a shareholder
- **Detailed Holdings**: Shares held, percentage ownership, and changes
- **Ticker Links**: Direct navigation from holder details to ticker information

### 🆕 Database Enhancements
- **New Fields**: Added `holder_type` and `hold_change` to holder records
- **Batch Processing**: Commits every 500 tickers for better performance
- **Individual Shareholder View**: SQL view for filtering 自然人 shareholders

## Quick Start

### 1. Environment Setup

The project is already set up with all dependencies installed. The virtual environment is located at `./venv/`.

### 2. Configure Tushare Token

The Tushare token has been pre-configured in `.env` file:
```
TUSHARE_TOKEN=a482999a9317dc55907b39ad983c2d43e6fb18c57563dc8e4b1369e6
```

### 3. Start the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Start the Flask application
python app.py
```

The application will be available at: http://localhost:5000

### 4. Initialize Data (First Run)

```bash
# Update all ticker and holder data
source venv/bin/activate
python -c "
from services.data_service import DataService
service = DataService()
success, message = service.update_all_data()
print(message)
service.close()
"
```

## Web Interface

1. **Home Page** (`/`): View individual shareholders (自然人) with ticker counts
2. **Shareholder Details** (`/holder/<holder_name>`): View all holdings for a specific shareholder
3. **Ticker Details** (`/ticker/<ts_code>`): View top 10 holders for a specific ticker

## API Endpoints

- `GET /api/holders` - Get individual shareholders with ticker counts
- `GET /api/holders/<holder_name>/tickers` - Get all holdings for a specific shareholder
- `GET /api/tickers/<ts_code>/holders` - Get top 10 holders for a specific ticker
- `GET /api/update-info` - Get latest update information
- `POST /api/update-data` - Manually trigger data update
- `GET /api/health` - Health check endpoint

### API Endpoints

- `GET /api/tickers` - Get all tickers with holder counts
- `GET /api/tickers/<ts_code>/holders` - Get top 10 holders for a specific ticker
- `POST /api/update-data` - Manually trigger data update
- `GET /api/health` - Health check endpoint

### Manual Data Updates

You can manually update data by:
1. Clicking "Update Data" button in the web interface
2. Running the update script: `python scripts/update_data.py`

## Project Structure

```
insightofstock/
├── app.py                 # Main Flask application
├── models.py             # SQLAlchemy database models
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── technical_design.md   # Technical design document
├── business_requirements.txt  # Original requirements
├── implementation_steps.md    # Implementation steps
├── services/             # Business logic
│   ├── __init__.py
│   ├── tushare_service.py    # Tushare API integration
│   └── data_service.py       # Data processing
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── ticker_detail.html    # Ticker detail page
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── main.js       # JavaScript functionality
├── scripts/              # Utility scripts
│   ├── init_db.py        # Database initialization
│   ├── update_data.py    # Daily data update script
│   └── setup_cron.py     # Cron job setup
├── database/             # Database files
│   └── insightofstock.db # SQLite database
└── venv/                 # Virtual environment
```

## Database Schema

### Tickers Table
- `id`: Primary key
- `ts_code`: Tushare stock code (unique)
- `symbol`: Stock symbol
- `name`: Company name
- `area`: Geographic area
- `industry`: Industry classification
- `list_date`: Listing date
- `updated_date`: Last update timestamp

### Top Holders Table
- `id`: Primary key
- `ts_code`: Foreign key to tickers
- `ann_date`: Announcement date
- `end_date`: Reporting period end date
- `holder_name`: Shareholder name
- `hold_amount`: Number of shares held
- `hold_ratio`: Percentage of shares held
- `holder_type`: Type of shareholder (e.g., 自然人, 机构, 基金)
- `hold_change`: Change in holdings
- `updated_date`: Last update timestamp

### Individual Shareholder View
- **View Name**: `individual_holder_tickers`
- **Purpose**: SQL view for filtering individual shareholders (自然人)
- **Columns**: `holder_name`, `ticker_count`

## Daily Updates

### Cron Job Setup (Linux/Mac)

```bash
# Run the setup script
python scripts/setup_cron.py

# Or manually add to crontab
echo "0 8 * * * cd $(pwd) && python scripts/update_data.py >> /tmp/insightofstock_cron.log 2>>1" | crontab -
```

### Systemd Timer (Linux)

For more reliable scheduling, use systemd timer:

```bash
# Create service files (need sudo)
sudo python scripts/setup_cron.py
```

### Check Update Logs

```bash
# View recent updates
tail -f /tmp/insightofstock_update.log

# View cron logs
tail -f /tmp/insightofstock_cron.log
```

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `app.py`
2. **Frontend**: Create new templates or modify existing ones
3. **Database**: Update models in `models.py`
4. **Services**: Extend functionality in `services/`

### Testing API Endpoints

```bash
# Test tickers endpoint
curl http://localhost:5000/api/tickers

# Test specific ticker holders
curl http://localhost:5000/api/tickers/000001.SZ/holders

# Test health check
curl http://localhost:5000/api/health
```

## Troubleshooting

### Common Issues

1. **Tushare Token Error**: Ensure `TUSHARE_TOKEN` is set in `.env`
2. **Database Issues**: Run `python scripts/init_db.py` to recreate tables
3. **Port Already in Use**: Change port with `PORT=8080 python app.py`
4. **Permission Errors**: Ensure scripts are executable with `chmod +x`

### Debug Mode

```bash
# Run with debug enabled
FLASK_DEBUG=True python app.py
```

### Reset Database

```bash
# Remove existing database
rm database/insightofstock.db

# Recreate database
python scripts/init_db.py

# Re-populate data
python scripts/update_data.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TUSHARE_TOKEN` | Tushare API token | (required) |
| `FLASK_ENV` | Flask environment | development |
| `FLASK_DEBUG` | Enable debug mode | True |
| `DATABASE_URL` | Database connection | sqlite:///database/insightofstock.db |
| `PORT` | Application port | 5000 |

## Data Sources

- **Tushare API**: Provides Chinese stock market data
- **Stock Basic Info**: `stock_basic` endpoint
- **Top 10 Holders**: `top10_holders` endpoint

## Performance Notes

- **Initial Load**: ~5,400 tickers with ~54,000 holder records
- **Update Time**: ~10-15 minutes for full update
- **Database Size**: ~10-20 MB for full dataset
- **API Rate Limits**: Tushare has daily query limits

## License

This project is created for educational purposes. Data provided by Tushare under their terms of service.