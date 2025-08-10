from flask import Flask, render_template, jsonify, request
from services.data_service import DataService
# from models import create_tables
import os
from dotenv import load_dotenv
from datetime import datetime

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
        # Check if we should filter for individual holders only
        individual_only = request.args.get('individual_only', 'false').lower() == 'true'
        individual_only = 'True'
        
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
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5001)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
