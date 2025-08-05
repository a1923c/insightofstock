from flask import Flask, render_template, jsonify, request
from services.data_service import DataService
from models import create_tables
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Handle subdirectory deployment
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize database
create_tables()

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
        
        from sqlalchemy import text
        
        if multiple_holders:
            # Use the new view for tickers with multiple holders, joining with tickers table
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
            
            count_query = text("""
                SELECT COUNT(*) 
                FROM tickers_with_multiple_holders
                WHERE holder_count >= :min_holders
            """)
        else:
            # Original query for all tickers
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
            
            count_query = text("SELECT COUNT(*) FROM tickers")
        
        offset = (page - 1) * per_page
        
        # Execute main query
        result = service.session.execute(query, {
            'min_holders': min_holders,
            'limit': per_page,
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
        
        # Get total count for pagination
        if multiple_holders:
            total_count = service.session.execute(count_query, {'min_holders': min_holders}).scalar()
        else:
            total_count = service.session.execute(count_query).scalar()
        
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
        from sqlalchemy import text, or_
        
        # Check if we should filter for individual holders only
        individual_only = request.args.get('individual_only', 'false').lower() == 'true'

        individual_only = 'true'
        
        # Get ticker info first
        ticker_query = text("SELECT ts_code, symbol, name, area, industry, list_date FROM tickers WHERE ts_code = :ts_code")
        ticker_result = service.session.execute(ticker_query, {'ts_code': ts_code}).fetchone()
        
        if not ticker_result:
            return jsonify({
                'success': False,
                'error': 'Ticker not found'
            }), 404
        
        ticker_info = {
            'ts_code': ticker_result[0],
            'symbol': ticker_result[1] or '-',
            'name': ticker_result[2],
            'area': ticker_result[3] or '',
            'industry': ticker_result[4] or '',
            'list_date': ticker_result[5]
        }
        
        # Get latest date for holders
        latest_date_query = text("SELECT MAX(end_date) FROM top_holders WHERE ts_code = :ts_code")
        latest_date_result = service.session.execute(latest_date_query, {'ts_code': ts_code}).fetchone()
        latest_date = latest_date_result[0] if latest_date_result else None
        
        if not latest_date:
            return jsonify({
                'success': False,
                'error': 'No holder data available'
            }), 404
        
        # Build query for holders
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
        
        holders_result = service.session.execute(holders_query, {
            'ts_code': ts_code,
            'end_date': latest_date
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
        
        # If individual_only and no individual holders found, return all holders as fallback
        if individual_only and len(holders) == 0:
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
            
            holders_result = service.session.execute(holders_query, {
                'ts_code': ts_code,
                'end_date': latest_date
            })
            
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
        
        # Query the individual_holder_tickers view
        from sqlalchemy import text
        
        # Get total count first
        count_query = text("""
            SELECT COUNT(*) 
            FROM individual_holder_tickers
            WHERE ticker_count >= 2
        """)
        total_count = service.session.execute(count_query).scalar()
        
        # Get paginated results
        query = text("""
            SELECT holder_name, ticker_count
            FROM individual_holder_tickers
            WHERE ticker_count >= 2
            ORDER BY ticker_count DESC, holder_name ASC
            LIMIT :limit OFFSET :offset
        """)
        
        offset = (page - 1) * per_page
        result = service.session.execute(query, {
            'limit': per_page,
            'offset': offset
        })
        
        holders = []
        for row in result:
            holders.append({
                'holder_name': row[0],
                'ticker_count': row[1]
            })
        
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
        from sqlalchemy import text
        
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
        
        result = service.session.execute(query, {'holder_name': holder_name})
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
        
        from sqlalchemy import text
        
        # Get total count first
        count_query = text("SELECT COUNT(*) FROM hm_list")
        total_count = service.session.execute(count_query).scalar()
        
        # Get paginated results
        query = text("""
            SELECT id, name, "desc", orgs
            FROM hm_list
            ORDER BY name ASC
            LIMIT :limit OFFSET :offset
        """)
        
        offset = (page - 1) * per_page
        result = service.session.execute(query, {
            'limit': per_page,
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
        from sqlalchemy import text
        
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
        
        result = service.session.execute(query, {'player_name': player_name})
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
