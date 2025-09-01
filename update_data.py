#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timezone
import argparse
import time
import sqlite3

# Import necessary models
from models import get_session, Ticker, TopHolder, UpdateLog, HmList, HmDetail, BalanceSheet, CashFlow, IncomeStatement, FinaIndicator, DailyBasic, ThsHot, DcHot, LastDayQuarter, Daily, AdjFactor, Dividend, IndexDaily
from services.tushare_service import TushareService
from utils.date_utils import get_date_n_days_ago
# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Table descriptions
TABLE_DESCRIPTIONS = {
    'tickers': 'Stock ticker information and basic company details',
    'top_holders': 'Top shareholders data for each stock',
    'hm_list': 'Market players/institutions list',
    'hm_detail': 'Player transaction details and activities',
    'balance_sheets': 'Financial balance sheets data',
    'cash_flows': 'Cash flow statements',
    'income_statements': 'Income and profit statements',
    'fina_indicators': 'Key financial indicators and ratios',
    'daily_basic': 'Daily basic market data and trading info',
    'ths_hot': 'THS hot concept and theme data',
    'dc_hot': 'DC hot concept and market attention data',
    'daily': 'daily quotes',
    'adj_factor': 'adjustment factor for stock price',
    'dividend': 'dividend data',
    'index_daily': 'index daily quotes'
}

def log_update(session, update_type, record_count):
    """Log updates to the update_log table"""
    try:
        last_update_date_str = datetime.now().strftime('%Y%m%d')
        log_entry = UpdateLog(
            update_type=update_type,
            last_update_date=last_update_date_str,
            record_count=record_count,
            updated_at=datetime.now(timezone.utc)
        )
        session.add(log_entry)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"{Colors.FAIL}Error logging update for {update_type}: {e}{Colors.ENDC}")

def interactive_table_selection():
    """Display interactive table selection menu"""
    print(f"\n{Colors.HEADER}=== Interactive Table Selection ==={Colors.ENDC}")
    print("Available tables for data update:\n")
    
    table_names = list(TABLE_DESCRIPTIONS.keys())
    
    for i, table_name in enumerate(table_names, 1):
        description = TABLE_DESCRIPTIONS[table_name]
        print(f"{Colors.OKGREEN}{i}. {table_name}{Colors.ENDC} - {description}")
    
    print(f"\n{Colors.WARNING}0. Exit without updating{Colors.ENDC}")
    print(f"{Colors.OKBLUE}a. Update all tables{Colors.ENDC}")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Enter your choice (numbers separated by commas, 'a' for all, or '0' to exit): {Colors.ENDC}").strip()
            
            if choice.lower() == '0':
                return None
            elif choice.lower() == 'a':
                return table_names
            elif choice.lower() == '':
                print(f"{Colors.WARNING}Please make a selection or enter '0' to exit.{Colors.ENDC}")
                continue
            
            selected_indices = []
            for part in choice.split(','):
                part = part.strip()
                if part.isdigit():
                    idx = int(part)
                    if 1 <= idx <= len(table_names):
                        selected_indices.append(idx - 1)
                    else:
                        print(f"{Colors.FAIL}Invalid number: {idx}. Please choose between 1 and {len(table_names)}.{Colors.ENDC}")
                        break
            else:
                if selected_indices:
                    selected_tables = [table_names[i] for i in selected_indices]
                    return selected_tables
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Operation cancelled by user.{Colors.ENDC}")
            return None
        except Exception as e:
            print(f"{Colors.FAIL}Invalid input: {e}{Colors.ENDC}")

def confirm_table_selection(tables):
    """Confirm table selection with user"""
    if not tables:
        return False
    
    print(f"\n{Colors.HEADER}=== Confirmation ==={Colors.ENDC}")
    print(f"Selected tables for update:")
    for table in tables:
        print(f"  - {Colors.OKGREEN}{table}{Colors.ENDC}: {TABLE_DESCRIPTIONS[table]}")
    
    try:
        confirm = input(f"\n{Colors.BOLD}Proceed with updating these {len(tables)} table(s)? (y/n): {Colors.ENDC}").strip().lower()
        return confirm == 'y' or confirm == 'yes'
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Operation cancelled by user.{Colors.ENDC}")
        return False

# Update functions for each table type
def update_tickers_data():
    """Update ticker information - insert all data directly"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching tickers from Tushare...{Colors.ENDC}")
        tickers_data = tushare_service.get_all_tickers()
        
        if not tickers_data:
            return False, "No ticker data fetched"
        
        count = 0
        for ticker_data in tickers_data:
            if not ticker_data.get('ts_code'):
                continue
            
            # Add updated_date to track when this data was loaded
            ticker_data['updated_date'] = datetime.now(timezone.utc)
            new_ticker = Ticker(**ticker_data)
            session.add(new_ticker)
            count += 1
        
        session.commit()
        log_update(session, 'tickers', count)
        return True, f"Inserted {count} tickers"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_top_holders_data():
    """Update top holders data"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching top holders data...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        
        if not all_tickers:
            return False, "No tickers found"
        
        total_records = 0
        ticker_count = 0
        for ticker in all_tickers:
            ticker_count += 1
            holders_data = tushare_service.get_top_holders(ticker.ts_code)
            if not holders_data:
                continue
            
            for holder_data in holders_data:
                holder_data['updated_date'] = datetime.now(timezone.utc)
                new_holder = TopHolder(**holder_data)
                session.add(new_holder)
                total_records += 1
            # Pause for 50 seconds after every 500 tickers。There is limitation of 500 Tushare API calling/every minute. 
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers. Pausing for 50 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
        
        session.commit()
        log_update(session, 'top_holders', total_records)
        return True, f"Inserted {total_records} holders"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_hm_list_data():
    """Update market players list"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching market players data...{Colors.ENDC}")
        hm_list_data = tushare_service.get_hm_list()
        
        if not hm_list_data:
            return False, "No market player data fetched"
        
        count = 0
        for data in hm_list_data:
            data['updated_date'] = datetime.now(timezone.utc)
            new_hm = HmList(**data)
            session.add(new_hm)
            count += 1
        
        session.commit()
        log_update(session, 'hm_list', count)
        return True, f"Inserted {count} market players"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_hm_detail_data():
    """Update market player transaction details"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching market player details...{Colors.ENDC}")
        all_players = session.query(HmList).all()
        
        if not all_players:
            return False, "No market players found"
        
        total_records = 0
        
        for player in all_players:
            details_data = tushare_service.get_hm_detail(player.name)
            if not details_data:
                continue
            
            for detail_data in details_data:
                detail_data['updated_date'] = datetime.now(timezone.utc)
                new_detail = HmDetail(**detail_data)
                session.add(new_detail)
                total_records += 1
        
        session.commit()
        log_update(session, 'hm_detail', total_records)
        return True, f"Inserted {total_records} player details"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_balance_sheets_data():
    """Update balance sheets data"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching balance sheets...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        last_day = session.query(LastDayQuarter).first()
        if not all_tickers or not last_day:
            return False, "No tickers found or no defined end_date"
        
        total_records = 0
        ticker_count = 0
        end_date = last_day.end_date

        # Delete existing records with end_date = last_day
        deleted_count = session.query(BalanceSheet).filter(BalanceSheet.end_date == end_date).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing balance sheet records with end_date={end_date}{Colors.ENDC}")
        

        for ticker in all_tickers:
            ticker_count += 1
            # Pause for 50 seconds after every 500 tickers。There is limitation of 500 Tushare API calling/every minute. 
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers with end_date{end_date}. Pausing for 50 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
            balance_data = tushare_service.get_balance_sheet(ticker.ts_code, end_date)
            if not balance_data:
                continue
            
            for data in balance_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_balance = BalanceSheet(**data)
                session.add(new_balance)
                total_records += 1
            
            
            
        session.commit()
        log_update(session, 'balance_sheets', total_records)
        return True, f"Inserted {total_records} balance sheets"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_cash_flows_data():
    """Update cash flow statements"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching cash flow statements...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        last_day = session.query(LastDayQuarter).first()
        if not all_tickers or not last_day:
            return False, "No tickers found or no defined end_date"
        
        total_records = 0
        ticker_count = 0
        end_date = last_day.end_date

        # Delete existing records with end_date = last_day
        deleted_count = session.query(CashFlow).filter(CashFlow.end_date == end_date).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing cash flow records with end_date={end_date}{Colors.ENDC}")

        for ticker in all_tickers:
            ticker_count += 1
            # Pause for 50 seconds after every 500 tickers。There is limitation of 500 Tushare API calling/every minute. 
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers with end_date={end_date}. Pausing for 50 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
            
            cash_flow_data = tushare_service.get_cash_flow(ticker.ts_code, end_date)
            if not cash_flow_data:
                continue
            
            for data in cash_flow_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_cash_flow = CashFlow(**data)
                session.add(new_cash_flow)
                total_records += 1
        
        session.commit()
        log_update(session, 'cash_flows', total_records)
        return True, f"Inserted {total_records} cash flow statements"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_income_statements_data():
    """Update income statements"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching income statements...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        last_day = session.query(LastDayQuarter).first()
        if not all_tickers or not last_day:
            return False, "No tickers found or no defined end_date"
        
        total_records = 0
        ticker_count = 0
        end_date = last_day.end_date

        # Delete existing records with end_date = last_day
        deleted_count = session.query(IncomeStatement).filter(IncomeStatement.end_date == end_date).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing income statement records with end_date={end_date}{Colors.ENDC}")

        for ticker in all_tickers:
            ticker_count += 1
            # Pause for 50 seconds after every 500 tickers。There is limitation of 500 Tushare API calling/every minute. 
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers with end_date={end_date}. Pausing for 50 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
            
            income_data = tushare_service.get_income_statement(ticker.ts_code, end_date)
            if not income_data:
                continue
            
            for data in income_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_income = IncomeStatement(**data)
                session.add(new_income)
                total_records += 1
        
        session.commit()
        log_update(session, 'income_statements', total_records)
        return True, f"Inserted {total_records} income statements"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_fina_indicators_data():
    """Update financial indicators"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching financial indicators...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        
        if not all_tickers:
            return False, "No tickers found"
        
        total_records = 0
        for ticker in all_tickers:
            indicators_data = tushare_service.get_fina_indicator(ticker.ts_code)
            if not indicators_data:
                continue
            
            for data in indicators_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_indicator = FinaIndicator(**data)
                session.add(new_indicator)
                total_records += 1
        
        session.commit()
        log_update(session, 'fina_indicators', total_records)
        return True, f"Inserted {total_records} financial indicators"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_daily_basic_data():
    """Update daily basic market data"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching daily basic data...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        
        if not all_tickers:
            return False, "No tickers found"
        
        total_records = 0
        ticker_count = 0
        trade_date = datetime.now().strftime("%Y%m%d")     # as end_date
        start_date = get_date_n_days_ago(5)  
        deleted_count = session.query(DailyBasic).filter(DailyBasic.trade_date >= start_date).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing daily basic records with trade_date={trade_date}{Colors.ENDC}")

        for ticker in all_tickers:
            # Pause for 50 seconds after every 700 tickers。There is limitation of 700 Tushare API calling/every minute. 
          
            daily_data = tushare_service.get_daily_basic(ticker.ts_code, start_date=start_date, end_date=trade_date)
            if not daily_data:
                continue
            
            for data in daily_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_daily = DailyBasic(**data)
                session.add(new_daily)
                total_records += 1
                if total_records % 500 == 0:
                    print(f"{Colors.WARNING}Processed {total_records} records.{Colors.ENDC}")
            ticker_count +=1
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers with start_date={start_date} and end_date={trade_date}. Pausing for 50 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(55)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")                      
        
        session.commit()
        log_update(session, 'daily_basic', total_records)
        return True, f"Inserted {total_records} daily basic records"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_ths_hot_data():
    """Update THS hot concept data"""
    session = get_session()
    tushare_service = TushareService()
    trade_date=datetime.now().strftime("%Y%m%d") 
    try:
        print(f"{Colors.OKBLUE}Fetching THS hot concept data...{Colors.ENDC}")
        ths_data = tushare_service.get_ths_hot(trade_date)
        
        if not ths_data:
            return False, "No THS hot data fetched"
        
        total_records = 0
        for data in ths_data:
            data['updated_date'] = datetime.now(timezone.utc)
            new_ths = ThsHot(**data)
            session.add(new_ths)
            total_records += 1
        
        session.commit()
        log_update(session, 'ths_hot', total_records)
        return True, f"Inserted {total_records} 同花顺 hot records for trade_date = {trade_date}"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_dc_hot_data():
    """Update DC hot concept data"""
    session = get_session()
    tushare_service = TushareService()
    trade_date=datetime.now().strftime("%Y%m%d") 
    try:
        print(f"{Colors.OKBLUE}Fetching DC hot concept data...{Colors.ENDC}")
        dc_data = tushare_service.get_dc_hot(trade_date)
        
        if not dc_data:
            return False, "No DC hot data fetched"
        
        count = 0
        for data in dc_data:
            data['updated_date'] = datetime.now(timezone.utc)
            new_dc = DcHot(**data)
            session.add(new_dc)
            count += 1
        
        session.commit()
        log_update(session, 'dc_hot', count)
        return True, f"Inserted {count} 东方财富 hot records for trade_date = {trade_date}"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_daily_data():
    """Update daily stock quotes and trading data for recent 360 days"""
    session = get_session()
    tushare_service = TushareService()
    
    try:
        print(f"{Colors.OKBLUE}Fetching daily stock quotes...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        
        if not all_tickers:
            return False, "No tickers found"
        
        total_records = 0
        ticker_count = 0
        
        # Get recent 360 days of data
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = get_date_n_days_ago(360)
        
        # Delete existing records in the date range to avoid duplicates
        deleted_count = session.query(Daily).filter(
            Daily.trade_date >= start_date,
            Daily.trade_date <= end_date
        ).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing daily records for date range {start_date} to {end_date}{Colors.ENDC}")

        for ticker in all_tickers:
            ticker_count += 1
            
            # Fetch daily data for this ticker
            daily_data = tushare_service.get_daily(ticker.ts_code, start_date=start_date, end_date=end_date)
            if not daily_data:
                continue
            
            # Insert new records
            for data in daily_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_daily = Daily(**data)
                session.add(new_daily)
                total_records += 1
            
            # Progress reporting
            if ticker_count % 100 == 0:
                print(f"{Colors.OKBLUE}Processed {ticker_count} tickers, inserted {total_records} daily records{Colors.ENDC}")
            
            # Rate limiting - pause every 500 tickers
            if ticker_count % 500 == 0:
                print(f"{Colors.WARNING}Processed {ticker_count} tickers. Pausing for 60 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
        
        session.commit()
        log_update(session, 'daily_data', total_records)
        return True, f"Inserted {total_records} daily stock quotes for recent 360 days"
        
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()
def update_adj_factor_data():
    """Update adjustment factor data for all tickers for recent 360 days"""
    session = get_session()
    tushare_service = TushareService()
    try:
        print(f"{Colors.OKBLUE}Fetching adj_factor data...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        if not all_tickers:
            return False, "No tickers found"
        total_records = 0
        ticker_count = 0
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = get_date_n_days_ago(360)
        deleted_count = session.query(AdjFactor).filter(
            AdjFactor.trade_date >= start_date,
            AdjFactor.trade_date <= end_date
        ).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing adj_factor records for date range {start_date} to {end_date}{Colors.ENDC}")
        for ticker in all_tickers:
            ticker_count += 1
            adj_data = tushare_service.get_adj_factor(ticker.ts_code, trade_date='')
            if not adj_data:
                continue
            for data in adj_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_adj = AdjFactor(**data)
                session.add(new_adj)
                total_records += 1
            if ticker_count % 500 == 0:
                session.commit()
                print(f"{Colors.OKBLUE}Committed after {ticker_count} tickers, total {total_records} adj_factor records so far.{Colors.ENDC}")
                # Optional: pause to avoid rate limiting
                print(f"{Colors.WARNING}Pausing for 60 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")

        session.commit()
        log_update(session, 'adj_factor', total_records)
        return True, f"Inserted {total_records} adj_factor records for recent 360 days"
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

def update_dividend_data():
    """Update dividend data for all tickers"""
    session = get_session()
    tushare_service = TushareService()
    try:
        print(f"{Colors.OKBLUE}Fetching dividend data...{Colors.ENDC}")
        all_tickers = session.query(Ticker).all()
        if not all_tickers:
            return False, "No tickers found"
        total_records = 0
        ticker_count = 0
        for ticker in all_tickers:
            ticker_count += 1
            dividend_data = tushare_service.get_dividend(ts_code=ticker.ts_code)
            if not dividend_data:
                continue
            for data in dividend_data:
                data['updated_date'] = datetime.now(timezone.utc)
                new_div = Dividend(**data)
                session.add(new_div)
                total_records += 1
            if ticker_count % 500 == 0:
                session.commit()
                print(f"{Colors.OKBLUE}Committed after {ticker_count} tickers, total {total_records} dividend records so far.{Colors.ENDC}")
                print(f"{Colors.WARNING}Pausing for 60 seconds to prevent API rate limiting...{Colors.ENDC}")
                time.sleep(60)
                print(f"{Colors.OKGREEN}Resuming data fetch...{Colors.ENDC}")
        session.commit()
        log_update(session, 'dividend', total_records)
        return True, f"Inserted {total_records} dividend records"
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

# Add to UPDATE_FUNCTIONS mapping:

def update_index_daily_data():
    """Update benchmark index daily data for 000300.SH for recent 360 days"""
    session = get_session()
    tushare_service = TushareService()
    try:
        print(f"{Colors.OKBLUE}Fetching index daily data for 000300.SH...{Colors.ENDC}")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = get_date_n_days_ago(360)
        deleted_count = session.query(IndexDaily).filter(
            IndexDaily.ts_code == '000300.SH',
            IndexDaily.trade_date >= start_date,
            IndexDaily.trade_date <= end_date
        ).delete()
        print(f"{Colors.WARNING}Deleted {deleted_count} existing index daily records for date range {start_date} to {end_date}{Colors.ENDC}")
        index_data = tushare_service.get_index_daily(ts_code='000300.SH', start_date=start_date, end_date=end_date)
        total_records = 0
        for data in index_data:
            data['updated_date'] = datetime.now(timezone.utc)
            new_index = IndexDaily(**data)
            session.add(new_index)
            total_records += 1
        session.commit()
        log_update(session, 'index_daily', total_records)
        return True, f"Inserted {total_records} index daily records for 000300.SH"
    except Exception as e:
        session.rollback()
        return False, f"Error: {e}"
    finally:
        session.close()

# Mapping of table names to update functions
UPDATE_FUNCTIONS = {
    'tickers': update_tickers_data,
    'top_holders': update_top_holders_data,
    'hm_list': update_hm_list_data,
    'hm_detail': update_hm_detail_data,
    'balance_sheets': update_balance_sheets_data,
    'cash_flows': update_cash_flows_data,
    'income_statements': update_income_statements_data,
    'fina_indicators': update_fina_indicators_data,
    'daily_basic': update_daily_basic_data,
    'ths_hot': update_ths_hot_data,
    'dc_hot': update_dc_hot_data,
    'daily':update_daily_data,
    'adj_factor': update_adj_factor_data,
    'dividend': update_dividend_data,
    'index_daily': update_index_daily_data
}

def main():
    """Main function to handle command line arguments and execute updates"""
    parser = argparse.ArgumentParser(description='Update stock market data from Tushare')
    parser.add_argument('--table', '-t', choices=list(UPDATE_FUNCTIONS.keys()), 
                       help='Specific table to update')
    parser.add_argument('--all', '-a', action='store_true', 
                       help='Update all tables')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive mode to select tables')
    
    args = parser.parse_args()
    
    print(f"{Colors.HEADER}=== Stock Market Data Updater ==={Colors.ENDC}")
    print(f"{Colors.OKBLUE}Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
    
    # Determine which tables to update
    tables_to_update = []
    
    if args.interactive:
        tables_to_update = interactive_table_selection()
        if tables_to_update is None:
            print(f"{Colors.WARNING}No tables selected. Exiting.{Colors.ENDC}")
            return
    elif args.all:
        tables_to_update = list(UPDATE_FUNCTIONS.keys())
    elif args.table:
        tables_to_update = [args.table]
    else:
        # Default to interactive mode if no arguments provided
        tables_to_update = interactive_table_selection()
        if tables_to_update is None:
            print(f"{Colors.WARNING}No tables selected. Exiting.{Colors.ENDC}")
            return
    
    if not confirm_table_selection(tables_to_update):
        print(f"{Colors.WARNING}Update cancelled by user.{Colors.ENDC}")
        return
    
    # Execute updates
    print(f"\n{Colors.HEADER}=== Starting Updates ==={Colors.ENDC}")
    
    success_count = 0
    total_tables = len(tables_to_update)
    
    for i, table_name in enumerate(tables_to_update, 1):
        print(f"\n{Colors.OKBLUE}[{i}/{total_tables}] Updating {table_name}...{Colors.ENDC}")
        
        update_func = UPDATE_FUNCTIONS[table_name]
        success, message = update_func()
        
        if success:
            print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")
            success_count += 1
        else:
            print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")
    
    # Summary
    print(f"\n{Colors.HEADER}=== Update Summary ==={Colors.ENDC}")
    print(f"Total tables: {total_tables}")
    print(f"Successful: {Colors.OKGREEN}{success_count}{Colors.ENDC}")
    print(f"Failed: {Colors.FAIL}{total_tables - success_count}{Colors.ENDC}")
    
    if success_count == total_tables:
        print(f"{Colors.OKGREEN}All updates completed successfully!{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}Some updates failed. Check the logs above.{Colors.ENDC}")

if __name__ == "__main__":
    main()
