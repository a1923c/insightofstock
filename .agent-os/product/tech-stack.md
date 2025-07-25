# Technical Stack

> Last Updated: 2025-07-25
> Version: 1.0.0

## Application Framework
- **Framework**: Python Flask 3.1.1
- **Language**: Python 3.11+
- **Architecture**: Model-View-Controller (MVC) pattern

## Database System
- **Primary**: SQLite 3.x
- **ORM**: SQLAlchemy 2.0.41
- **Migration Tool**: Flask-Migrate (Alembic-based)
- **Connection Pooling**: SQLAlchemy connection pooling

## Data Integration
- **Primary Source**: Tushare API
- **API Client**: Official Tushare Python SDK
- **Update Frequency**: Daily automated via cron job
- **Data Volume**: ~54,000 holder records across 5,400+ tickers

## Frontend Stack
- **Structure**: HTML5 with semantic markup
- **Styling**: Bootstrap 5.x CSS framework
- **JavaScript**: Vanilla JavaScript for interactivity
- **Icons**: Bootstrap Icons
- **Responsive Design**: Mobile-first responsive layout

## Server Infrastructure
- **Application Server**: Gunicorn WSGI server
- **Web Server**: Nginx (reverse proxy, planned)
- **Process Management**: Systemd service (planned)
- **SSL/TLS**: Let's Encrypt (planned)

## Development Environment
- **Package Management**: pip with requirements.txt
- **Virtual Environment**: venv (standard Python)
- **Development Server**: Flask built-in development server
- **Database Management**: SQLite CLI tools, SQLAlchemy utilities

## Background Processing
- **Scheduler**: Linux cron jobs
- **Update Scripts**: Python data synchronization scripts
- **Logging**: Python logging module with file rotation
- **Error Handling**: Comprehensive exception handling with logging

## Security (Planned)
- **Authentication**: Flask-Login for user accounts
- **Authorization**: Role-based access control
- **Input Validation**: WTForms with server-side validation
- **Rate Limiting**: Flask-Limiter (planned)

## Monitoring (Planned)
- **Application Monitoring**: Basic logging and error tracking
- **Database Monitoring**: Query performance monitoring
- **Uptime Monitoring**: External service integration
- **Data Quality**: Automated data validation scripts