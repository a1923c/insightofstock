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
    """Home page showing all tickers"""
    return render_template('index.html')

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
            # Use the new view for tickers with multiple holders
            query = text("""
                SELECT 
                    ts_code,
                    symbol,
                    name,
                    area,
                    industry,
                    list_date,
                    holder_count,
                    latest_holder_date
                FROM tickers_with_multiple_holders
                WHERE holder_count >= :min_holders
                ORDER BY holder_count DESC, name ASC
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
                'holder_count': row[6] or 0,
                'latest_holder_date': row[7]
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
    """Get top 10 holders for a specific ticker"""
    service = DataService()
    try:
        ticker_info, error = service.get_ticker_holders(ts_code)
        if error:
            return jsonify({
                'success': False,
                'error': error
            }), 404
        
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
        # Query the individual_holder_tickers view
        from sqlalchemy import text
        
        query = text("""
            SELECT holder_name, ticker_count
            FROM individual_holder_tickers
            WHERE ticker_count >= 2
        """)
        
        result = service.session.execute(query)
        holders = []
        for row in result:
            holders.append({
                'holder_name': row[0],
                'ticker_count': row[1]
            })
        
        return jsonify({
            'success': True,
            'data': holders,
            'count': len(holders)
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
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5001)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )