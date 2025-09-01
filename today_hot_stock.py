#!/usr/bin/env python3
"""
Today Hot Stocks Venn Diagram Display
A standalone script to display today's hot stocks using a Venn diagram metaphor
with fancy animations and interactive features.
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os
from pathlib import Path

class HotStocksVenn:
    def __init__(self, db_path='database/insightofstock.db'):
        """Initialize with database connection"""
        self.db_path = db_path
        self.ths_stocks = []
        self.dc_stocks = []
        self.intersection = []
        
    def fetch_hot_stocks(self):
        """Fetch today's hot stocks from both THS and DC sources"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get today's date in format YYYYMMDD
            today = datetime.now().strftime('%Y%m%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
            week_ago='20250813'
            
            print(f"DEBUG: Using date filter: {week_ago}")
            
            # Fetch THS hot stocks with proper NULL handling
            ths_query = """
                SELECT DISTINCT ts_code, ts_name, concept, 
                       COALESCE(CAST(pct_change AS REAL), 0.0) as pct_change, 
                       COALESCE(CAST(current_price AS REAL), 0.0) as current_price, 
                       COALESCE(CAST(hot AS REAL), 0.0) as hot
                FROM ths_hot 
                WHERE data_type='热股' 
                AND trade_date >= ? 
                AND ts_code IS NOT NULL 
                AND ts_name IS NOT NULL
                AND ts_code != ''
                AND ts_name != ''
                ORDER BY COALESCE(CAST(hot AS REAL), 0.0) DESC
                LIMIT 20
            """
            print(f"DEBUG: THS Query: {ths_query}")
            print(f"DEBUG: THS Parameters: {week_ago}")
            cursor.execute(ths_query, (week_ago,))
            self.ths_stocks = cursor.fetchall()
            print(f"DEBUG: THS stocks found: {len(self.ths_stocks)}")
            
            # Fetch DC hot stocks with proper NULL handling
            dc_query = """
                SELECT DISTINCT ts_code, ts_name, concept, 
                       COALESCE(CAST(pct_change AS REAL), 0.0) as pct_change, 
                       COALESCE(CAST(current_price AS REAL), 0.0) as current_price, 
                       COALESCE(CAST("rank" AS REAL), 0.0) as rank
                FROM dc_hot 
                WHERE data_type='A股市场' 
                AND trade_date >= ?
                AND ts_code IS NOT NULL 
                AND ts_name IS NOT NULL
                AND ts_code != ''
                AND ts_name != ''
                ORDER BY COALESCE(CAST("rank" AS REAL), 0.0) DESC
                LIMIT 20
            """
            print(f"DEBUG: DC Query: {dc_query}")
            print(f"DEBUG: DC Parameters: {week_ago}")
            cursor.execute(dc_query, (week_ago,))
            self.dc_stocks = cursor.fetchall()
            print(f"DEBUG: DC stocks found: {len(self.dc_stocks)}")
            
            # Let's also try a simpler query to debug
            simple_dc_query = """
                SELECT COUNT(*) FROM dc_hot 
                WHERE data_type='A股市场' 
                AND trade_date >= ?
            """
            cursor.execute(simple_dc_query, (week_ago,))
            simple_count = cursor.fetchone()[0]
            print(f"DEBUG: Simple DC count: {simple_count}")
            
            # And check what data types we have
            sample_query = """
                SELECT ts_code, ts_name, concept, pct_change, current_price, "rank"
                FROM dc_hot 
                WHERE data_type='A股市场' 
                AND trade_date >= ?
                LIMIT 3
            """
            cursor.execute(sample_query, (week_ago,))
            sample_data = cursor.fetchall()
            print(f"DEBUG: Sample DC data: {sample_data}")
            
            conn.close()
            
            # Filter out any remaining None values - only filter if critical fields are None
            self.ths_stocks = [s for s in self.ths_stocks if s[0] is not None and s[1] is not None and s[0] != '' and s[1] != '']
            self.dc_stocks = [s for s in self.dc_stocks if s[0] is not None and s[1] is not None and s[0] != '' and s[1] != '']
            
            print(f"DEBUG: After filtering None values - THS: {len(self.ths_stocks)}, DC: {len(self.dc_stocks)}")
            
            # Calculate intersection (stocks appearing in both)
            ths_codes = {stock[0] for stock in self.ths_stocks}
            dc_codes = {stock[0] for stock in self.dc_stocks}
            intersection_codes = ths_codes.intersection(dc_codes)
            
            print(f"DEBUG: THS codes: {len(ths_codes)}")
            print(f"DEBUG: DC codes: {len(dc_codes)}")
            print(f"DEBUG: Intersection codes: {len(intersection_codes)}")
            print(f"DEBUG: Intersection codes: {list(intersection_codes)[:5]}")
            
            # Build intersection list with combined data
            self.intersection = []
            for code in intersection_codes:
                ths_data = next(s for s in self.ths_stocks if s[0] == code)
                dc_data = next(s for s in self.dc_stocks if s[0] == code)
                self.intersection.append({
                    'ts_code': code,
                    'ts_name': str(ths_data[1]),
                    'concept': f"{str(ths_data[2] or '')} | {str(dc_data[2] or '')}".strip(' |'),
                    'pct_change': (float(ths_data[3]) + float(dc_data[3])) / 2,
                    'current_price': float(ths_data[4]),
                    'hot': max(float(ths_data[5]), float(dc_data[5]))
                })
            
            # Filter out intersection from individual lists
            self.ths_only = [s for s in self.ths_stocks if s[0] not in intersection_codes]
            self.dc_only = [s for s in self.dc_stocks if s[0] not in intersection_codes]
            
            print(f"DEBUG: After intersection filtering - THS only: {len(self.ths_only)}, DC only: {len(self.dc_only)}")
            print(f"Successfully fetched {len(self.ths_stocks)} THS stocks and {len(self.dc_stocks)} DC stocks")
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            print("Using sample data for demonstration...")
            # Use sample data for demonstration
            self.use_sample_data()
    def use_sample_data(self):
        """Use sample data when database is not available"""
        self.ths_only = [
            ('000001.SZ', '平安银行', '银行', 5.2, 12.5, 85.3),
            ('000002.SZ', '万科A', '房地产', 3.8, 18.9, 78.9),
            ('600519.SH', '贵州茅台', '白酒', 2.1, 1678.5, 92.1)
        ]
        
        self.dc_only = [
            ('300750.SZ', '宁德时代', '新能源', 4.5, 245.8, 88.7),
            ('002594.SZ', '比亚迪', '汽车', 6.2, 198.5, 91.2),
            ('601012.SH', '隆基绿能', '光伏', 3.9, 28.4, 76.5)
        ]
        
        self.intersection = [
            {
                'ts_code': '000858.SZ',
                'ts_name': '五粮液',
                'concept': '白酒 | 消费',
                'pct_change': 4.8,
                'current_price': 156.7,
                'hot': 89.4
            },
            {
                'ts_code': '600036.SH',
                'ts_name': '招商银行',
                'concept': '银行 | 金融',
                'pct_change': 3.2,
                'current_price': 35.8,
                'hot': 82.1
            }
        ]
    
    def generate_html(self):
        """Generate the HTML with Venn diagram visualization"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>今日热门股票 - Venn图展示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .venn-container {{
            position: relative;
            width: 800px;
            height: 500px;
            margin: 0 auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .circle {{
            position: absolute;
            width: 400px;
            height: 400px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: all 0.3s ease;
            cursor: pointer;
            overflow: hidden;
        }}
        
        .circle-left {{
            left: 100px;
            background: radial-gradient(circle at 30% 30%, 
                rgba(255, 99, 132, 0.8) 0%, 
                rgba(255, 99, 132, 0.4) 50%, 
                rgba(255, 99, 132, 0.1) 100%);
            animation: fadeInLeft 1s ease-out;
        }}
        
        .circle-right {{
            right: 100px;
            background: radial-gradient(circle at 70% 30%, 
                rgba(54, 162, 235, 0.8) 0%, 
                rgba(54, 162, 235, 0.4) 50%, 
                rgba(54, 162, 235, 0.1) 100%);
            animation: fadeInRight 1s ease-out;
        }}
        
        .intersection {{
            position: absolute;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: radial-gradient(circle at 50% 50%, 
                rgba(255, 206, 86, 0.9) 0%, 
                rgba(255, 206, 86, 0.6) 50%, 
                rgba(255, 206, 86, 0.3) 100%);
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            animation: pulse 2s ease-in-out infinite;
            z-index: 10;
        }}
        
        .stock-item {{
            background: rgba(255, 255, 255, 0.9);
            margin: 5px;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            max-width: 150px;
            text-align: center;
        }}
        
        .stock-item:hover {{
            transform: scale(1.1);
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            background: rgba(255, 255, 255, 1);
        }}
        
        .stock-code {{
            font-weight: bold;
            color: #333;
        }}
        
        .stock-name {{
            color: #666;
            font-size: 11px;
        }}
        
        .stock-change {{
            font-size: 10px;
            color: #e74c3c;
        }}
        
        .circle-label {{
            position: absolute;
            top: 20px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            animation: fadeIn 0.3s ease;
        }}
        
        .modal-content {{
            background-color: white;
            margin: 10% auto;
            padding: 30px;
            border-radius: 15px;
            width: 400px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        }}
        
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{
            color: #000;
        }}
        
        .modal h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .modal-info {{
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        @keyframes fadeInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-50px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes fadeInRight {{
            from {{
                opacity: 0;
                transform: translateX(50px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}
        
        @keyframes pulse {{
            0% {{
                transform: translate(-50%, -50%) scale(1);
                opacity: 0.8;
            }}
            50% {{
                transform: translate(-50%, -50%) scale(1.05);
                opacity: 1;
            }}
            100% {{
                transform: translate(-50%, -50%) scale(1);
                opacity: 0.8;
            }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateY(-50px);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}
        
        .legend {{
            text-align: center;
            margin-top: 40px;
            color: white;
        }}
        
        .legend-item {{
            display: inline-block;
            margin: 0 20px;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        .legend-ths {{
            background: rgba(255, 99, 132, 0.8);
            color: white;
        }}
        
        .legend-dc {{
            background: rgba(54, 162, 235, 0.8);
            color: white;
        }}
        
        .legend-intersection {{
            background: rgba(255, 206, 86, 0.9);
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>今日热门股票 Venn图</h1>
        
        <div class="venn-container">
            <div class="circle circle-left">
                <div class="circle-label">THS 热门</div>
                {self.generate_stock_items(self.ths_only, 'ths')}
            </div>
            
            <div class="circle circle-right">
                <div class="circle-label">DC 热门</div>
                {self.generate_stock_items(self.dc_only, 'dc')}
            </div>
            
            <div class="intersection">
                <div class="circle-label">双重热门</div>
                {self.generate_intersection_items(self.intersection)}
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item legend-ths">THS: 同花顺热门股票</div>
            <div class="legend-item legend-dc">DC: 东方财富热门股票</div>
            <div class="legend-item legend-intersection">交集: 双重热门股票</div>
        </div>
    </div>
    
    <!-- Modal -->
    <div id="stockModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2 id="modalTitle">股票详情</h2>
            <div id="modalBody"></div>
        </div>
    </div>
    
    <script>
        // Modal functionality
        const modal = document.getElementById('stockModal');
        const closeBtn = document.getElementsByClassName('close')[0];
        
        function showModal(stockData) {{
            document.getElementById('modalTitle').textContent = `${{stockData.name}} (${{stockData.code}})`;
            
            let content = `
                <div class="modal-info">
                    <strong>当前价格:</strong> ¥${{stockData.price}}
                </div>
                <div class="modal-info">
                    <strong>涨跌幅:</strong> <span style="color: ${{(stockData.change >= 0) ? '#e74c3c' : '#27ae60'}}">${{stockData.change}}%</span>
                </div>
                <div class="modal-info">
                    <strong>热度值:</strong> ${{stockData.hot}}
                </div>
                <div class="modal-info">
                    <strong>概念标签:</strong> ${{stockData.concept}}
                </div>
                <div class="modal-info">
                    <strong>更新时间:</strong> ${{(new Date()).toLocaleString('zh-CN')}}
                </div>
            `;
            
            document.getElementById('modalBody').innerHTML = content;
            modal.style.display = 'block';
        }}
        
        closeBtn.onclick = function() {{
            modal.style.display = 'none';
        }}
        
        window.onclick = function(event) {{
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
        
        // Add click handlers to stock items
        document.querySelectorAll('.stock-item').forEach(item => {{
            item.addEventListener('click', function() {{
                const stockData = {{
                    code: this.dataset.code,
                    name: this.dataset.name,
                    price: this.dataset.price,
                    change: this.dataset.change,
                    hot: this.dataset.hot,
                    concept: this.dataset.concept
                }};
                showModal(stockData);
            }});
        }});
        
        // Add hover effects
        document.querySelectorAll('.circle').forEach(circle => {{
            circle.addEventListener('mouseenter', function() {{
                this.style.transform = 'scale(1.02)';
            }});
            
            circle.addEventListener('mouseleave', function() {{
                this.style.transform = 'scale(1)';
            }});
        }});
    </script>
</body>
</html>
"""
        return html_content
    
    def generate_stock_items(self, stocks, source):
        """Generate HTML for stock items"""
        items = []
        for stock in stocks:
            code, name, concept, change, price, hot = stock
            items.append(f'''
                <div class="stock-item" 
                     data-code="{code}" 
                     data-name="{name}" 
                     data-price="{price:.2f}" 
                     data-change="{change:.2f}" 
                     data-hot="{hot:.1f}" 
                     data-concept="{concept}">
                    <div class="stock-code">{code}</div>
                    <div class="stock-name">{name}</div>
                    <div class="stock-change">{change:+.2f}%</div>
                </div>
            ''')
        return '\n'.join(items)
    
    def generate_intersection_items(self, stocks):
        """Generate HTML for intersection items"""
        items = []
        for stock in stocks:
            items.append(f'''
                <div class="stock-item" 
                     data-code="{stock['ts_code']}" 
                     data-name="{stock['ts_name']}" 
                     data-price="{stock['current_price']:.2f}" 
                     data-change="{stock['pct_change']:.2f}" 
                     data-hot="{stock['hot']:.1f}" 
                     data-concept="{stock['concept']}">
                    <div class="stock-code">{stock['ts_code']}</div>
                    <div class="stock-name">{stock['ts_name']}</div>
                    <div class="stock-change">{stock['pct_change']:+.2f}%</div>
                </div>
            ''')
        return '\n'.join(items)
    
    def save_html(self, filename='today_hot_stocks.html'):
        """Save the generated HTML to file"""
        html_content = self.generate_html()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML file saved as: {filename}")
        return filename
    
    def run(self):
        """Main execution method"""
        print("Fetching today's hot stocks...")
        self.fetch_hot_stocks()
        
        print(f"THS stocks: {len(self.ths_only)}")
        print(f"DC stocks: {len(self.dc_only)}")
        print(f"Intersection: {len(self.intersection)}")
        
        filename = self.save_html()
        return filename

if __name__ == "__main__":
    # Check if database exists
    db_path = 'database/insightofstock.db'
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}, using sample data...")
    
    venn = HotStocksVenn(db_path)
    html_file = venn.run()
    
    # Try to open in browser
    try:
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath(html_file)}')
        print("Opening in browser...")
    except:
        print(f"Please open {html_file} in your browser manually.")
