import os
import tushare as ts
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv('/var/www/insightofstock/.env')

class TushareService:
    def __init__(self):
        self.token = os.getenv('TUSHARE_TOKEN')
        if not self.token:
            raise ValueError("TUSHARE_TOKEN not found in environment variables")
        
        ts.set_token(self.token)
        self.pro = ts.pro_api()
    
    def get_all_tickers(self):
        """Get all stock tickers from Tushare"""
        try:
            # Get all stocks from A-share market
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            tickers = []
            for _, row in df.iterrows():
                tickers.append({
                    'ts_code': row['ts_code'],
                    'symbol': row['symbol'],
                    'name': row['name'],
                    'area': row['area'] or '',
                    'industry': row['industry'] or '',
                    'list_date': str(row['list_date']) if pd.notna(row['list_date']) else ''
                })
            
            return tickers
            
        except Exception as e:
            print(f"Error fetching tickers: {e}")
            return []
    
    def get_top_holders(self, ts_code, limit=10):
        """Get top 10 holders for a specific ticker"""
        try:
            # Get the latest report date
            end_date = datetime.now().strftime('%Y%m%d')
            
            # Get top 10 individual holders (流通股东)
            df = self.pro.top10_floatholders(
                ts_code=ts_code,
                end_date='',
                fields='ts_code,ann_date,end_date,holder_name,hold_amount,hold_ratio,holder_type,hold_change'
            )
            
            if df.empty:
                return []
            
            # Sort by end_date desc and take top 10
            df = df.sort_values('end_date', ascending=False)
            latest_end_date = df['end_date'].iloc[0]
            df = df[df['end_date'] == latest_end_date].head(limit)
            
            # Convert DataFrame to list of dictionaries
            holders = []
            for _, row in df.iterrows():
                holders.append({
                    'ts_code': row['ts_code'],
                    'ann_date': str(row['ann_date']) if pd.notna(row['ann_date']) else '',
                    'end_date': str(row['end_date']) if pd.notna(row['end_date']) else '',
                    'holder_name': row['holder_name'] or '',
                    'hold_amount': float(row['hold_amount']) if pd.notna(row['hold_amount']) else 0.0,
                    'hold_ratio': float(row['hold_ratio']) if pd.notna(row['hold_ratio']) else 0.0,
                    'holder_type': row['holder_type'] or '',
                    'hold_change': float(row['hold_change']) if pd.notna(row['hold_change']) else 0.0
                })
            
            return holders
            
        except Exception as e:
            print(f"Error fetching top holders for {ts_code}: {e}")
            return []
    
    def update_all_data(self):
        """Update all ticker and holder data"""
        tickers = self.get_all_tickers()
        if not tickers:
            return False, "Failed to fetch tickers"
        
        results = {
            'tickers_updated': len(tickers),
            'holders_updated': 0,
            'errors': []
        }
        
        for ticker in tickers:
            try:
                holders = self.get_top_holders(ticker['ts_code'])
                results['holders_updated'] += len(holders)
            except Exception as e:
                results['errors'].append(f"Error updating {ticker['ts_code']}: {str(e)}")
        
        return True, results

if __name__ == "__main__":
    # Test the service
    service = TushareService()
    tickers = service.get_all_tickers()
    print(f"Found {len(tickers)} tickers")
    
    if tickers:
        sample_ticker = tickers[0]
        holders = service.get_top_holders(sample_ticker['ts_code'])
        print(f"Sample ticker: {sample_ticker['name']} - {len(holders)} holders found")