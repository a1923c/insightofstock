from models import get_session, Ticker, TopHolder, UpdateLog
from services.tushare_service import TushareService
from datetime import datetime

class DataService:
    def __init__(self):
        self.session = get_session()
        self.tushare_service = TushareService()
    
    def get_latest_holder_date(self):
        """Get the latest end_date from top_holders table"""
        latest = self.session.query(TopHolder.end_date).order_by(TopHolder.end_date.desc()).first()
        return latest[0] if latest else None
    
    def log_update(self, update_type, last_update_date, record_count=0):
        """Log the latest update date"""
        log_entry = UpdateLog(
            update_type=update_type,
            last_update_date=last_update_date,
            record_count=record_count
        )
        self.session.merge(log_entry)  # Use merge to update existing entry
        self.session.commit()
    
    def update_tickers(self):
        """Update all tickers from Tushare"""
        try:
            tickers_data = self.tushare_service.get_all_tickers()
            updated_count = 0
            
            for ticker_data in tickers_data:
                ticker = self.session.query(Ticker).filter_by(ts_code=ticker_data['ts_code']).first()
                
                if not ticker:
                    ticker = Ticker(**ticker_data)
                    self.session.add(ticker)
                    updated_count += 1
                else:
                    # Update existing ticker
                    for key, value in ticker_data.items():
                        setattr(ticker, key, value)
                    updated_count += 1
            
            self.session.commit()
            
            # Log update
            self.log_update('tickers', datetime.now().strftime('%Y%m%d'), updated_count)
            return True, f"Updated {updated_count} tickers"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def update_top_holders(self, ts_code=None):
        """Update top holders for specific ticker or all tickers with batch commits (500 tickers)"""
        try:
            if ts_code:
                # Update specific ticker
                tickers = self.session.query(Ticker).filter_by(ts_code=ts_code).all()
            else:
                # Update all tickers
                tickers = self.session.query(Ticker).all()
            
            total_updated_count = 0
            latest_end_date = None
            
            print(f"📊 Starting update for {len(tickers)} tickers with batch commits (500 tickers)...")
            
            # Initialize batch session
            batch_session = get_session()
            processed_count = 0
            
            for i, ticker in enumerate(tickers, 1):
                try:
                    # Print ticker name during loading
                    print(f"📋 Processing {i}/{len(tickers)}: {ticker.ts_code} - {ticker.name}...")
                    
                    # Get new holders from Tushare
                    holders_data = self.tushare_service.get_top_holders(ticker.ts_code)
                    
                    if holders_data:
                        # Get the latest end_date from the data
                        current_latest = max(h['end_date'] for h in holders_data)
                        if not latest_end_date or current_latest > latest_end_date:
                            latest_end_date = current_latest
                        
                        # Clear existing holders for this ticker
                        batch_session.query(TopHolder).filter_by(ts_code=ticker.ts_code).delete()
                        
                        # Add new holders
                        for holder_data in holders_data:
                            holder = TopHolder(**holder_data)
                            batch_session.add(holder)
                        
                        total_updated_count += len(holders_data)
                        processed_count += 1
                    
                    # Commit every 500 tickers
                    if processed_count >= 500:
                        batch_session.commit()
                        print(f"✅ Committed batch: {processed_count} tickers processed, {total_updated_count} holders total")
                        
                        # Start new batch session
                        batch_session.close()
                        batch_session = get_session()
                        processed_count = 0
                    
                    if i % 100 == 0:
                        print(f"📊 Processed {i}/{len(tickers)} tickers ({total_updated_count} holders total)")
                    
                except Exception as ticker_error:
                    print(f"❌ Error updating {ticker.ts_code}: {ticker_error}")
                    continue
            
            # Commit remaining data
            if processed_count > 0:
                batch_session.commit()
                print(f"✅ Final commit: {processed_count} tickers processed")
            
            batch_session.close()
            
            # Log update with latest date
            if latest_end_date:
                self.log_update('holders', latest_end_date, total_updated_count)
            
            print(f"✅ Completed: Updated {total_updated_count} holder records across {len(tickers)} tickers")
            return True, f"Updated {total_updated_count} holder records across {len(tickers)} tickers"
            
        except Exception as e:
            return False, str(e)
    
    def get_latest_update_info(self):
        """Get the latest update information"""
        tickers_update = self.session.query(UpdateLog).filter_by(update_type='tickers').first()
        holders_update = self.session.query(UpdateLog).filter_by(update_type='holders').first()
        
        # If no holders update, use tickers update date as fallback
        holders_date = holders_update.last_update_date if holders_update else tickers_update.last_update_date if tickers_update else None
        
        return {
            'tickers': {
                'last_update_date': tickers_update.last_update_date if tickers_update else None,
                'updated_at': tickers_update.updated_at.isoformat() if tickers_update else None,
                'record_count': tickers_update.record_count if tickers_update else 0
            },
            'holders': {
                'last_update_date': holders_date,
                'updated_at': holders_update.updated_at.isoformat() if holders_update else tickers_update.updated_at.isoformat() if tickers_update else None,
                'record_count': holders_update.record_count if holders_update else 0
            }
        }
    
    def get_all_tickers(self):
        """Get all tickers with holder count"""
        try:
            tickers = self.session.query(Ticker).all()
            result = []
            
            for ticker in tickers:
                # Get holder count for latest date
                latest_date = self.get_latest_holder_date()
                if latest_date:
                    holder_count = self.session.query(TopHolder).filter_by(
                        ts_code=ticker.ts_code, 
                        end_date=latest_date
                    ).count()
                else:
                    holder_count = 0
                
                result.append({
                    'ts_code': ticker.ts_code,
                    'symbol': ticker.symbol,
                    'name': ticker.name,
                    'area': ticker.area,
                    'industry': ticker.industry,
                    'list_date': ticker.list_date,
                    'holder_count': holder_count,
                    'updated_date': ticker.updated_date.strftime('%Y-%m-%d %H:%M:%S') if ticker.updated_date else None
                })
            
            return result
            
        except Exception as e:
            return []
    
    def get_ticker_holders(self, ts_code):
        """Get top holders for a specific ticker using latest date"""
        try:
            ticker = self.session.query(Ticker).filter_by(ts_code=ts_code).first()
            if not ticker:
                return None, "Ticker not found"
            
            # Get latest date for holders
            latest_date = self.get_latest_holder_date()
            if not latest_date:
                return None, "No holder data available"
            
            holders = []
            for holder in self.session.query(TopHolder).filter_by(
                ts_code=ticker.ts_code, 
                end_date=latest_date
            ).order_by(TopHolder.hold_ratio.desc()).all():
                holders.append({
                    'ann_date': holder.ann_date,
                    'end_date': holder.end_date,
                    'holder_name': holder.holder_name,
                    'hold_amount': holder.hold_amount,
                    'hold_ratio': holder.hold_ratio,
                    'holder_type': holder.holder_type,
                    'hold_change': holder.hold_change,
                    'updated_date': holder.updated_date.strftime('%Y-%m-%d %H:%M:%S') if holder.updated_date else None
                })
            
            ticker_info = {
                'ts_code': ticker.ts_code,
                'symbol': ticker.symbol,
                'name': ticker.name,
                'area': ticker.area,
                'industry': ticker.industry,
                'list_date': ticker.list_date,
                'holders': holders,
                'latest_holder_date': latest_date
            }
            
            return ticker_info, None
            
        except Exception as e:
            return None, str(e)
    
    def update_all_data(self):
        """Update all ticker and holder data"""
        try:
            # Update tickers first
            success, message = self.update_tickers()
            if not success:
                return False, message
            
            # Then update holders
            success, message = self.update_top_holders()
            if not success:
                return False, message
            
            return True, "All data updated successfully"
            
        except Exception as e:
            return False, str(e)
    
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