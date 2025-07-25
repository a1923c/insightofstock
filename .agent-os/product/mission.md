# Product Mission

> Last Updated: 2025-07-25
> Version: 1.0.0

## Pitch

Insight of Stock is a financial analytics platform that helps individual investors and financial analysts research Chinese stock market private shareholders by providing comprehensive portfolio analysis and shareholder intelligence not available on traditional price/volume platforms.

## Users

### Primary Customers

- **Individual Investors**: Retail investors looking to leverage shareholder intelligence for investment decisions
- **Financial Analysts**: Professionals tracking shareholder patterns and market concentration trends
- **Market Researchers**: Academics and institutions studying private shareholder behavior and market dynamics
- **Private Portfolio Managers**: Managers building portfolios based on following top individual shareholder strategies

### User Personas

**Sophisticated Individual Investor** (30-50 years old)
- **Role**: Full-time private investor or semi-professional trader
- **Context**: Manages personal portfolio of ¥100K-¥1M+ actively seeking alpha through unique data insights
- **Pain Points**: Limited visibility into individual shareholder movements, can't track "smart money" in Chinese markets, existing platforms focus only on institutional holders
- **Goals**: Identify successful individual investors to follow, understand market concentration risks, find emerging opportunities before they hit mainstream platforms

**Financial Research Analyst** (25-45 years old)
- **Role**: Equity research analyst at brokerage or investment firm
- **Context**: Produces research reports on Chinese equities and market structure
- **Pain Points**: Lacks granular data on individual shareholder composition, manual data collection from multiple sources, time-intensive analysis
- **Goals**: Access comprehensive shareholder databases, generate insights on market concentration, identify trending stocks through shareholder changes

## The Problem

### The Visibility Gap in Chinese Markets

Individual shareholders represent a significant portion of Chinese stock market ownership (>60% by some estimates), yet existing platforms provide almost no visibility into this crucial demographic. Traditional financial platforms focus exclusively on institutional holders and price/volume data, leaving a massive blind spot for investors trying to understand who actually owns Chinese stocks.

**Our Solution**: Comprehensive database and analysis platform focused specifically on individual (自然人) shareholders, providing portfolio tracking, concentration analysis, and trend identification capabilities.

### Data Fragmentation and Manual Research Burden

Investors currently rely on fragmented quarterly reports, manual PDF analysis, and scattered disclosure documents to track individual shareholder movements. This process is time-intensive, error-prone, and incomplete.

**Our Solution**: Automated daily data collection from Tushare API with real-time updates, eliminating manual research burden while providing comprehensive coverage.

## Differentiators

### Individual Shareholder Focus

Unlike Bloomberg, Wind, or other financial platforms that focus on institutional ownership and price data, we exclusively track individual (自然人) shareholders. This provides unique insights into the behavior of China's most successful private investors who often outperform institutional funds.

### Real-Time Comprehensive Database

Our platform maintains a live database of ~54,000 individual holder records across 5,400+ Chinese tickers, updated daily via automated Tushare API integration. This represents the most comprehensive individual shareholder database available for Chinese markets.

### Drill-Down Intelligence

While other platforms show top 10 holders as a static list, we provide interactive drill-down capabilities that allow users to explore individual portfolios, track changes over time, and analyze concentration patterns across holdings.

## Key Features

### Core Features

- **Individual Shareholder Database**: Comprehensive tracking of all individual (自然人) shareholders in Chinese markets with portfolio composition analysis
- **Real-Time Data Updates**: Daily automated synchronization from Tushare API ensuring current information
- **Portfolio Drill-Down**: Interactive exploration from shareholder lists to detailed individual holdings
- **Ticker Analysis**: Detailed shareholder composition for any Chinese stock with concentration metrics
- **Search and Filtering**: Advanced filtering by shareholder name, ticker, position size, and change patterns

### Analytics Features

- **Market Concentration Analysis**: Identify heavily concentrated vs. diversified ownership patterns
- **Trending Shareholders**: Track which individual investors are increasing/decreasing positions
- **Portfolio Overlap Detection**: Identify stocks held by multiple successful individual investors
- **Historical Position Tracking**: Monitor how individual shareholder positions evolve over time

### Future Collaboration Features

- **User Accounts and Watchlists**: Personal accounts to save favorite shareholders and stocks for monitoring
- **Export Functionality**: Download shareholder data and analysis for offline research
- **Historical Trend Analysis**: Long-term tracking of shareholder behavior patterns
- **Alert System**: Notifications when tracked shareholders make significant position changes