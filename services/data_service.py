from flask import Flask, render_template, jsonify, request
from services.tushare_service import TushareService
from models import create_tables
import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import text, or_ # Import text and or_

# Import all models that might be used in the new methods
from models import get_session, Ticker, TopHolder, UpdateLog, HmList, HmDetail, BalanceSheet, CashFlow, IncomeStatement, FinaIndicator, DailyBasic, ThsHot, DcHot

load_dotenv()

# Explicitly set the database URL to ensure the correct database is used
# This assumes the database file is located at /Users/admin_gu/insightofstock/database/insightofstock.db
os.environ['DATABASE_URL'] = 'sqlite:///database/insightofstock.db'

app = Flask(__name__)

# Handle subdirectory deployment
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database
# create_tables()

@app.route('/')
def index():
    """Home page with tabs for individual holders and tickers with multiple holders"""
    return render_template('index.html')

@app.route('/multiple-holders')
def multiple_holders():
    """Page showing tickers with multiple individual holders"""
    return render_template('multiple_holders.html')

@app.route('/ticker/<ts_code>')
def ticker_detail(ts_code):
    """Ticker detail page showing holders"""
    return render_template('ticker_detail.html', ts_code=ts_code)

# API Endpoints
@app.route('/api/tickers')
def api_tickers():
    """Get tickers with holder count, optionally filtered by multiple holders"""
    service = DataService()
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        multiple_holders = request.args.get('multiple_holders', 'false').lower() == 'true'
        min_holders = int(request.args.get('min_holders', 2))
        
        if multiple_holders:
            tickers = service.get_tickers_with_multiple_holders(min_holders, per_page, (page - 1) * per_page)
            total_count = service.count_tickers_with_multiple_holders(min_holders)
        else:
            tickers = service.get_all_tickers_paginated(per_page, (page - 1) * per_page)
            total_count = service.count_all_tickers()
        
        update_info = service.get_latest_update_info()
        
        return jsonify({
            'success': True,
            'data': tickers,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            },
            'latest_update': update_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/tickers/<ts_code>/holders')
def api_ticker_holders(ts_code):
    """Get top holders for a specific ticker using latest date"""
    service = DataService()
    try:
        # Get ticker info first
        ticker_info, error = service.get_ticker_info(ts_code)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 404
        
        # Get latest date for holders
        latest_date = service.get_latest_holder_date_for_ticker(ts_code)
        
        if not latest_date:
            return jsonify({
                'success': False,
                'error': 'No holder data available'
            }), 404
        
        # Check if we should filter for individual holders only
        individual_only = request.args.get('individual_only', 'false').lower() == 'true'
        
        holders, error = service.get_top_holders_for_ticker(ts_code, latest_date, individual_only)
        
        if error and individual_only: # If individual_only failed, try fallback
            print(f"Individual holders not found for {ts_code}, trying fallback.")
            holders, error = service.get_individual_holders_fallback(ts_code, latest_date)
            if error: # If fallback also failed, return error
                return jsonify({
                    'success': False,
                    'error': error
                }), 500
        elif error: # If not individual_only and error occurred
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        ticker_info['holders'] = holders
        ticker_info['latest_holder_date'] = latest_date
        
        update_info = service.get_latest_update_info()
        return jsonify({
            'success': True,
            'data': ticker_info,
            'latest_update': update_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/update-data', methods=['POST'])
def api_update_data():
    """Manual trigger for data update"""
    service = DataService()
    try:
        success, message = service.update_all_data()
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/holders')
def api_holders():
    """Get individual shareholders with ticker count using the database view"""
    service = DataService()
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        total_count = service.count_individual_holder_tickers()
        holders = service.get_individual_holder_tickers_paginated(per_page, (page - 1) * per_page)
        
        return jsonify({
            'success': True,
            'data': holders,
            'count': len(holders),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/holder/<holder_name>')
def holder_detail(holder_name):
    """Holder detail page showing all tickers owned"""
    return render_template('holder_detail.html', holder_name=holder_name)

@app.route('/player/<player_name>')
def player_detail(player_name):
    """Player detail page showing all transactions"""
    return render_template('player_detail.html', player_name=player_name)

@app.route('/api/holders/<path:holder_name>/tickers')
def api_holder_tickers(holder_name):
    """Get all tickers and holdings for a specific holder"""
    service = DataService()
    try:
        tickers = service.get_holder_tickers(holder_name)
        
        return jsonify({
            'success': True,
            'data': {
                'holder_name': holder_name,
                'tickers': tickers
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/market-players')
def api_market_players():
    """Get market players"""
    service = DataService()
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        total_count = service.count_hm_list()
        players = service.get_hm_list_paginated(per_page, (page - 1) * per_page)
        
        return jsonify({
            'success': True,
            'data': players,
            'count': len(players),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/market-players/<path:player_name>/transactions')
def api_player_transactions(player_name):
    """Get all transactions for a specific market player"""
    service = DataService()
    try:
        transactions = service.get_player_transactions(player_name)
        
        return jsonify({
            'success': True,
            'data': {
                'player_name': player_name,
                'transactions': transactions
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

# New route for Recent Hot Stocks
@app.route('/api/recent-hot-stocks')
def api_recent_hot_stocks():
    """Get recent hot stocks with ts_code and ts_name"""
    service = DataService()
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20)) # Defaulting to 20 per page, similar to market players
        
        total_count = service.count_recent_hot_stocks()
        hot_stocks = service.get_recent_hot_stocks_paginated(per_page, (page - 1) * per_page)
        
        return jsonify({
            'success': True,
            'data': hot_stocks,
            'count': len(hot_stocks),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/update-info')
def api_update_info():
    """Get latest update information"""
    service = DataService()
    try:
        update_info = service.get_latest_update_info()
        return jsonify({
            'success': True,
            'data': update_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

@app.route('/api/financial-reports/<ts_code>')
def api_financial_reports(ts_code):
    """Get financial reports for a specific ticker"""
    service = DataService()
    try:
        # Get optional end_date parameter
        end_date = request.args.get('end_date', None)
        
        reports = service.get_financial_reports(ts_code, end_date)
        if reports:
            return jsonify({
                'success': True,
                'data': reports
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No financial reports found for this ticker'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        service.close()

# --- New methods for DataService ---
class DataService:
    def __init__(self):
        self.session = get_session()
        self.tushare_service = TushareService()
    
    # Existing methods (get_latest_holder_date, log_update, update_tickers, etc.) are kept here
    # ... (omitted for brevity, assume they are present) ...

    # --- New methods for API endpoints ---

    # For api_tickers
    def get_tickers_with_multiple_holders(self, min_holders, limit, offset):
        query = text("""
            SELECT 
                tmh.ts_code,
                t.symbol,
                t.name,
                t.area,
                t.industry,
                t.list_date,
                tmh.holder_count
            FROM tickers_with_multiple_holders tmh
            JOIN tickers t ON tmh.ts_code = t.ts_code
            WHERE tmh.holder_count >= :min_holders
            ORDER BY tmh.holder_count DESC, t.name ASC
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.execute(query, {
            'min_holders': min_holders,
            'limit': limit,
            'offset': offset
        })
        
        tickers = []
        for row in result:
            tickers.append({
                'ts_code': row[0],
                'symbol': row[1] or '-',
                'name': row[2],
                'area': row[3] or '',
                'industry': row[4] or '',
                'list_date': row[5],
                'holder_count': row[6] or 0
            })
        return tickers

    def count_tickers_with_multiple_holders(self, min_holders):
        query = text("""
            SELECT COUNT(*) 
            FROM tickers_with_multiple_holders
            WHERE holder_count >= :min_holders
        """)
        return self.session.execute(query, {'min_holders': min_holders}).scalar()

    def get_all_tickers_paginated(self, limit, offset):
        query = text("""
            SELECT 
                t.ts_code,
                t.symbol,
                t.name,
                t.area,
                t.industry,
                t.list_date,
                COUNT(DISTINCT h.holder_name) as holder_count,
                MAX(h.end_date) as latest_holder_date
            FROM tickers t
            LEFT JOIN top_holders h ON t.ts_code = h.ts_code 
                AND h.end_date = (
                    SELECT MAX(end_date) 
                    FROM top_holders 
                    WHERE ts_code = t.ts_code
                )
            GROUP BY t.ts_code, t.symbol, t.name, t.area, t.industry, t.list_date
            ORDER BY holder_count DESC, t.name ASC
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.execute(query, {
            'limit': limit,
            'offset': offset
        })
        
        tickers = []
        for row in result:
            tickers.append({
                'ts_code': row[0],
                'symbol': row[1] or '-',
                'name': row[2],
                'area': row[3] or '',
                'industry': row[4] or '',
                'list_date': row[5],
                'holder_count': row[6] or 0
            })
        return tickers

    def count_all_tickers(self):
        query = text("SELECT COUNT(*) FROM tickers")
        return self.session.execute(query).scalar()

    # For api_ticker_holders
    def get_ticker_info(self, ts_code):
        ticker_query = text("SELECT ts_code, symbol, name, area, industry, list_date FROM tickers WHERE ts_code = :ts_code")
        ticker_result = self.session.execute(ticker_query, {'ts_code': ts_code}).fetchone()
        
        if not ticker_result:
            return None, 'Ticker not found'
        
        ticker_info = {
            'ts_code': ticker_result[0],
            'symbol': ticker_result[1] or '-',
            'name': ticker_result[2],
            'area': ticker_result[3] or '',
            'industry': ticker_result[4] or '',
            'list_date': ticker_result[5]
        }
        return ticker_info, None

    def get_latest_holder_date_for_ticker(self, ts_code):
        latest_date_query = text("SELECT MAX(end_date) FROM top_holders WHERE ts_code = :ts_code")
        latest_date_result = self.session.execute(latest_date_query, {'ts_code': ts_code}).fetchone()
        return latest_date_result[0] if latest_date_result else None
    
    def get_top_holders_for_ticker(self, ts_code, end_date, individual_only=False):
        if individual_only:
            # Filter for individual holders with a broader filter
            holders_query = text("""
                SELECT 
                    ann_date,
                    end_date,
                    holder_name,
                    hold_amount,
                    hold_ratio,
                    holder_type,
                    hold_change
                FROM top_holders 
                WHERE ts_code = :ts_code 
                AND end_date = :end_date
                AND (
                    holder_type IS NULL OR 
                    holder_type = '' OR 
                    holder_type IN ('个人', 'G', '自然人', '个人股东')
                )
                ORDER BY hold_ratio DESC
            """)
        else:
            holders_query = text("""
                SELECT 
                    ann_date,
                    end_date,
                    holder_name,
                    hold_amount,
                    hold_ratio,
                    holder_type,
                    hold_change
                FROM top_holders 
                WHERE ts_code = :ts_code 
                AND end_date = :end_date
                ORDER BY hold_ratio DESC
            """)
        
        holders_result = self.session.execute(holders_query, {
            'ts_code': ts_code,
            'end_date': end_date
        })
        
        holders = []
        for row in holders_result:
            holders.append({
                'ann_date': row[0],
                'end_date': row[1],
                'holder_name': row[2],
                'hold_amount': row[3],
                'hold_ratio': row[4],
                'holder_type': row[5],
                'hold_change': row[6]
            })
        
        if not holders and individual_only:
            return [], "No individual holders found, fallback not implemented for this method yet." # Placeholder for fallback logic
        elif not holders:
            return [], None # No error if no holders found and not individual_only
        
        return holders, None

    def get_individual_holders_fallback(self, ts_code, end_date):
        # Fallback query for holders if individual_only filter yields no results
        holders_query = text("""
            SELECT 
                ann_date,
                end_date,
                holder_name,
                hold_amount,
                hold_ratio,
                holder_type,
                hold_change
            FROM top_holders 
            WHERE ts_code = :ts_code 
            AND end_date = :end_date
            ORDER BY hold_ratio DESC
        """)
        
        holders_result = self.session.execute(holders_query, {
            'ts_code': ts_code,
            'end_date': end_date
        })
        
        holders = []
        for row in holders_result:
            holders.append({
                'ann_date': row[0],
                'end_date': row[1],
                'holder_name': row[2],
                'hold_amount': row[3],
                'hold_ratio': row[4],
                'holder_type': row[5],
                'hold_change': row[6]
            })
        
        if not holders:
            return [], "No holders found even with fallback."
        
        return holders, None

    # For api_holders
    def count_individual_holder_tickers(self):
        count_query = text("""
            SELECT COUNT(*) 
            FROM individual_holder_tickers
            WHERE ticker_count >= 2
        """)
        return self.session.execute(count_query).scalar()

    def get_individual_holder_tickers_paginated(self, limit, offset):
        query = text("""
            SELECT holder_name, ticker_count
            FROM individual_holder_tickers
            WHERE ticker_count >= 2
            ORDER BY ticker_count DESC, holder_name ASC
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.execute(query, {
            'limit': limit,
            'offset': offset
        })
        
        holders = []
        for row in result:
            holders.append({
                'holder_name': row[0],
                'ticker_count': row[1]
            })
        return holders

    # For api_holder_tickers
    def get_holder_tickers(self, holder_name):
        query = text("""
            SELECT 
                t.ts_code,
                t.symbol,
                t.name,
                h.hold_amount,
                h.hold_ratio,
                h.hold_change,
                h.end_date
            FROM top_holders h
            JOIN tickers t ON h.ts_code = t.ts_code
            WHERE h.holder_name = :holder_name
            ORDER BY h.hold_ratio DESC
        """)
        result = self.session.execute(query, {'holder_name': holder_name})
        tickers = []
        for row in result:
            tickers.append({
                'ts_code': row[0],
                'symbol': row[1] or '-',
                'name': row[2],
                'hold_amount': row[3],
                'hold_ratio': row[4],
                'hold_change': row[5],
                'end_date': row[6]
            })
        return tickers

    # For api_market_players
    def count_hm_list(self):
        count_query = text("SELECT COUNT(*) FROM hm_list")
        return self.session.execute(count_query).scalar()

    def get_hm_list_paginated(self, limit, offset):
        query = text("""
            SELECT id, name, "desc", orgs
            FROM hm_list
            ORDER BY name ASC
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.execute(query, {
            'limit': limit,
            'offset': offset
        })
        
        players = []
        for row in result:
            players.append({
                'id': row[0],
                'name': row[1],
                'desc': row[2],
                'orgs': row[3]
            })
        return players

    # For api_player_transactions
    def get_player_transactions(self, player_name):
        query = text("""
            SELECT 
                trade_date,
                ts_code,
                ts_name,
                buy_amount,
                sell_amount,
                net_amount,
                orgs
            FROM hm_detail
            WHERE name = :player_name
            ORDER BY trade_date DESC
        """)
        result = self.session.execute(query, {'player_name': player_name})
        transactions = []
        for row in result:
            transactions.append({
                'trade_date': row[0],
                'ts_code': row[1],
                'ts_name': row[2],
                'buy_amount': row[3],
                'sell_amount': row[4],
                'net_amount': row[5],
                'orgs': row[6]
            })
        return transactions

    # For api_recent_hot_stocks
    def count_recent_hot_stocks(self):
        count_query = text("SELECT COUNT(DISTINCT ts_code) FROM recent_hot_stocks")
        return self.session.execute(count_query).scalar()

    def get_recent_hot_stocks_paginated(self, limit, offset):
        query = text("""
            SELECT DISTINCT ts_code, ts_name
            FROM recent_hot_stocks
            ORDER BY ts_code ASC -- Or any other relevant order
            LIMIT :limit OFFSET :offset
        """)
        result = self.session.execute(query, {
            'limit': limit,
            'offset': offset
        })
        
        hot_stocks = []
        for row in result:
            hot_stocks.append({
                'ts_code': row[0],
                'ts_name': row[1]
            })
        return hot_stocks

    def get_latest_update_info(self):
        """Get the latest update information from the UpdateLog table"""
        try:
            # Query for the latest log entry, ordered by updated_at
            latest_log = self.session.query(UpdateLog).order_by(UpdateLog.updated_at.desc()).first()
            
            if latest_log:
                # Safely retrieve attributes using getattr
                last_data_update = getattr(latest_log, 'last_update_date', None)
                
                log_timestamp = None
                updated_at_val = getattr(latest_log, 'updated_at', None)
                if updated_at_val:
                    # Ensure it's a datetime object before calling isoformat
                    if isinstance(updated_at_val, datetime):
                        log_timestamp = updated_at_val.isoformat()
                    else:
                        # Fallback if updated_at is not a datetime object
                        log_timestamp = str(updated_at_val) 
                
                return {
                    'last_data_update': last_data_update,
                    'log_timestamp': log_timestamp
                }
            else:
                # If no logs are found, return a specific message
                return {'message': 'No update logs found'}
        except Exception as e:
            # Log the error and return an error dictionary
            print(f"Error fetching latest update info: {e}")
            return {'error': str(e)}

    def close(self):
        """Close database session"""
        self.session.close()

if __name__ == "__main__":
    service = DataService()
    
    # Test ticker update
    success, message = service.update_tickers()
    print(f"Ticker update: {message}")
    
    # Test holder update
    success, message = service.update_top_holders()
    print(f"Holder update: {message}")
    
    # Test get all tickers
    tickers = service.get_all_tickers()
    print(f"Found {len(tickers)} tickers")
    
    service.close()
