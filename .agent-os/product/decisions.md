# Product Decisions Log

> Last Updated: 2025-07-25
> Version: 1.0.0
> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2025-07-25: Initial Product Planning and Architecture Decisions

**ID:** DEC-001
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Solo Developer, Market Research

### Decision

Insight of Stock will be a specialized financial analytics platform focused exclusively on individual (自然人) shareholders in the Chinese stock market, using real-time Tushare API data with daily automated updates and a Flask/SQLite architecture optimized for shareholder intelligence rather than traditional price/volume analysis.

### Context

The Chinese stock market has over 200 million individual investors who represent more than 60% of trading volume, yet existing platforms like Bloomberg, Wind, and local Chinese financial websites provide almost no visibility into individual shareholder portfolios and movements. This creates a significant market intelligence gap for both retail and institutional investors.

Traditional financial data providers focus on:
- Institutional holders (funds, insurance companies, etc.)
- Price and volume data
- Technical indicators
- Company fundamentals

However, they completely miss the individual shareholder layer, which includes:
- High-net-worth individuals with concentrated positions
- Successful retail investors whose strategies could be followed
- Market concentration risks from individual holders
- "Smart money" movements among top individual investors

### Alternatives Considered

1. **Broad Financial Platform Approach**
   - Pros: Larger total addressable market, can compete with existing platforms
   - Cons: Highly competitive market, requires significant resources, no clear differentiation

2. **Institutional Focus**
   - Pros: Higher revenue per customer, established sales channels
   - Cons: Longer sales cycles, requires enterprise sales team, regulatory complexity

3. **Price/Volume Analytics**
   - Pros: Familiar to investors, established metrics and indicators
   - Cons: Saturated market with excellent existing solutions

### Rationale

The individual shareholder focus creates a unique market position with several advantages:

1. **Blue Ocean Strategy**: No direct competitors focusing specifically on individual Chinese shareholders
2. **Data Advantage**: Tushare API provides comprehensive individual shareholder data that's underutilized
3. **Market Size**: 200M+ individual investors in China represent enormous potential user base
4. **Technical Feasibility**: Flask/SQLite architecture can handle current data volume (~54K records) while remaining scalable
5. **Monetization Path**: Clear progression from free basic features to premium analytics and eventually enterprise data feeds

### Consequences

**Positive:**
- Unique market positioning with no direct competitors
- Scalable data source (Tushare) with comprehensive coverage
- Clear technical architecture that supports current needs and future growth
- Strong foundation for premium features and enterprise expansion
- Addresses real pain point for Chinese market investors

**Negative:**
- Limited to Chinese market (initially)
- Dependent on Tushare API availability and pricing
- Requires educating market about value of individual shareholder data
- May need regulatory considerations for international users
- Database size will grow significantly over time (estimated 100K+ new records annually)

## 2025-07-25: Technical Architecture Decisions

**ID:** DEC-002
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Technical Lead, Solo Developer

### Decision

Implement with Python Flask 3.1.1 and SQLite database using SQLAlchemy ORM, prioritizing simplicity and rapid development over microservices or cloud-native architecture, with daily cron-based data updates from Tushare API.

### Context

As a solo developer building an MVP, the primary constraints are:
- Limited development time and resources
- Need to validate market demand quickly
- Must maintain low operational costs
- Should be easily deployable and maintainable

### Alternatives Considered

1. **Cloud-Native Architecture (AWS/GCP)**
   - Pros: Scalable, reliable, professional-grade infrastructure
   - Cons: Higher complexity, ongoing costs, vendor lock-in

2. **Microservices Architecture**
   - Pros: Scalable, maintainable for large teams
   - Cons: Overkill for MVP, complex deployment, resource intensive

3. **Django Framework**
   - Pros: Batteries included, large ecosystem, built-in admin
   - Cons: Heavier than needed, more opinionated structure

4. **PostgreSQL Database**
   - Pros: Enterprise-grade, scalable, robust
   - Cons: Additional setup complexity, resource requirements

### Rationale

Flask + SQLite provides the optimal balance for an MVP:
- **Development Speed**: Flask's minimal structure allows rapid prototyping
- **Resource Efficiency**: SQLite handles current data volume (54K records) efficiently
- **Deployment Simplicity**: Single server deployment with minimal configuration
- **Cost Effectiveness**: Zero database licensing costs
- **Migration Path**: Easy upgrade path to PostgreSQL when scaling

### Consequences

**Positive:**
- Rapid development and deployment
- Low operational costs during validation phase
- Simple maintenance and debugging
- Easy local development environment setup
- Clear upgrade path when scaling requirements emerge

**Negative:**
- Limited concurrent user capacity
- Database backup and recovery complexity
- No built-in horizontal scaling
- May require migration effort when user base grows

## 2025-07-25: Data Source and Update Strategy

**ID:** DEC-003
**Status:** Accepted
**Category:** Technical
**Stakeholders**: Technical Lead, Product Owner

### Decision

Use Tushare API as the primary data source with daily automated updates via cron job, accepting the limitations of free tier API limits and focusing on top 10 shareholders to maximize data quality and coverage within constraints.

### Context

Tushare provides the most comprehensive and accessible source of Chinese stock market data, including individual shareholder information. The free tier has rate limits but is sufficient for the MVP scope.

### Alternatives Considered

1. **Multiple Data Sources**
   - Pros: Redundancy, comprehensive coverage
   - Cons: Integration complexity, inconsistent data formats, higher costs

2. **Real-time Web Scraping**
   - Pros: Always current data, no API limits
   - Cons: Fragile, legally questionable, high maintenance burden

3. **Premium Data Feeds**
   - Pros: Higher quality, additional data fields
   - Cons: Significant monthly costs, long-term contracts

4. **Manual Data Collection**
   - Pros: Full control, custom data processing
   - Cons: Impossible to scale, human error prone

### Rationale

Tushare strikes the right balance for an MVP:
- **Data Quality**: Reliable, structured data from official sources
- **Cost**: Free tier sufficient for current needs
- **Coverage**: Comprehensive individual shareholder data
- **API Design**: Well-documented, Python-friendly
- **Community**: Active community and ongoing development

### Consequences

**Positive:**
- Reliable data source with consistent format
- Automated daily updates ensure data freshness
- Predictable API behavior and error handling
- Clear upgrade path to premium tiers when needed
- No upfront data costs during validation phase

**Negative:**
- Rate limiting may impact future scaling
- Dependent on Tushare's continued operation
- Limited to top 10 shareholders (current API limitation)
- No historical data beyond what's provided by API