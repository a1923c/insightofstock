from models import get_session, Ticker, TopHolder, UpdateLog, HmList, HmDetail, BalanceSheet, CashFlow, IncomeStatement
from services.tushare_service import TushareService
from datetime import datetime
from sqlalchemy import or_
from utils.date_utils import get_date_n_days_ago

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
    
    def get_ticker_holders(self, ts_code, individual_only=False):
        """Get top holders for a specific ticker using latest date"""
        try:
            ticker = self.session.query(Ticker).filter_by(ts_code=ts_code).first()
            if not ticker:
                return None, "Ticker not found"
            
            # Get latest date for holders
            latest_date = self.get_latest_holder_date()
            if not latest_date:
                return None, "No holder data available"
            
            # Build query
            query = self.session.query(TopHolder).filter_by(
                ts_code=ticker.ts_code, 
                end_date=latest_date
            )
            
            # Filter for individual holders if requested
            if individual_only:
                # First try to get individual holders with a broader filter
                # Include records where holder_type is null/empty (assume individual) or matches individual types
                individual_query = query.filter(
                    or_(
                        TopHolder.holder_type == None,
                        TopHolder.holder_type == '',
                        TopHolder.holder_type.in_(['个人', 'G', '自然人', '个人股东'])
                    )
                )
                holders = []
                for holder in individual_query.order_by(TopHolder.hold_ratio.desc()).all():
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
                
                # If no individual holders found, return all holders (fallback)
                if len(holders) == 0:
                    print(f"No individual holders found for {ts_code}, returning all holders")
                    query = self.session.query(TopHolder).filter_by(
                        ts_code=ticker.ts_code, 
                        end_date=latest_date
                    )
            else:
                holders = []
            
            # If we haven't populated holders yet (either not individual_only or fallback)
            if len(holders) == 0:
                for holder in query.order_by(TopHolder.hold_ratio.desc()).all():
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
    
    def update_hm_list(self):
        """Update hm_list data from Tushare"""
        try:
            hm_list_data = self.tushare_service.get_hm_list()
            updated_count = 0
            
            # Clear existing data
            self.session.query(HmList).delete()
            
            for item_data in hm_list_data:
                # Create new hm_list item
                item = HmList(**item_data)
                self.session.add(item)
                updated_count += 1
            
            self.session.commit()
            return True, f"Updated {updated_count} hm_list items"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def update_hm_detail(self):
        """Update hm_detail data from Tushare"""
        try:
            # Get all names from hm_list
            hm_list_items = self.session.query(HmList).all()
            
            # Calculate date range (180 days ago to today)
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = get_date_n_days_ago(180)
            
            total_updated_count = 0
            
            # Clear existing data
            self.session.query(HmDetail).delete()
            
            # Fetch hm_detail data for each name in hm_list
            for item in hm_list_items:
                try:
                    print(f"Fetching hm_detail data for {item.name}...")
                    hm_detail_data = self.tushare_service.get_hm_detail(
                        name=item.name,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Add new hm_detail items
                    for detail_data in hm_detail_data:
                        # Create new hm_detail item
                        detail_item = HmDetail(**detail_data)
                        self.session.add(detail_item)
                        total_updated_count += 1
                        
                except Exception as e:
                    print(f"Error fetching hm_detail data for {item.name}: {e}")
                    continue
            
            self.session.commit()
            return True, f"Updated {total_updated_count} hm_detail items"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def update_balance_sheets(self, ts_code=None):
        """Update balance sheets for specific ticker or all tickers"""
        try:
            if ts_code:
                # Update specific ticker
                tickers = self.session.query(Ticker).filter_by(ts_code=ts_code).all()
            else:
                # Update all tickers
                tickers = self.session.query(Ticker).all()
            
            total_updated_count = 0
            
            for i, ticker in enumerate(tickers, 1):
                try:
                    print(f"📋 Processing balance sheet {i}/{len(tickers)}: {ticker.ts_code} - {ticker.name}...")
                    
                    # Get balance sheet data from Tushare
                    balance_sheet_data = self.tushare_service.get_balance_sheet(ticker.ts_code)
                    
                    if balance_sheet_data:
                        # Clear existing balance sheets for this ticker
                        self.session.query(BalanceSheet).filter_by(ts_code=ticker.ts_code).delete()
                        
                        # Add new balance sheets
                        for data in balance_sheet_data:
                            balance_sheet = BalanceSheet(**data)
                            self.session.add(balance_sheet)
                        
                        total_updated_count += len(balance_sheet_data)
                        
                except Exception as ticker_error:
                    print(f"❌ Error updating balance sheet for {ticker.ts_code}: {ticker_error}")
                    continue
            
            self.session.commit()
            print(f"✅ Completed: Updated {total_updated_count} balance sheet records across {len(tickers)} tickers")
            return True, f"Updated {total_updated_count} balance sheet records across {len(tickers)} tickers"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def update_cash_flows(self, ts_code=None):
        """Update cash flows for specific ticker or all tickers"""
        try:
            if ts_code:
                # Update specific ticker
                tickers = self.session.query(Ticker).filter_by(ts_code=ts_code).all()
            else:
                # Update all tickers
                tickers = self.session.query(Ticker).all()
            
            total_updated_count = 0
            
            for i, ticker in enumerate(tickers, 1):
                try:
                    print(f"📋 Processing cash flow {i}/{len(tickers)}: {ticker.ts_code} - {ticker.name}...")
                    
                    # Get cash flow data from Tushare
                    cash_flow_data = self.tushare_service.get_cash_flow(ticker.ts_code)
                    
                    if cash_flow_data:
                        # Clear existing cash flows for this ticker
                        self.session.query(CashFlow).filter_by(ts_code=ticker.ts_code).delete()
                        
                        # Add new cash flows
                        for data in cash_flow_data:
                            cash_flow = CashFlow(**data)
                            self.session.add(cash_flow)
                        
                        total_updated_count += len(cash_flow_data)
                        
                except Exception as ticker_error:
                    print(f"❌ Error updating cash flow for {ticker.ts_code}: {ticker_error}")
                    continue
            
            self.session.commit()
            print(f"✅ Completed: Updated {total_updated_count} cash flow records across {len(tickers)} tickers")
            return True, f"Updated {total_updated_count} cash flow records across {len(tickers)} tickers"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def update_income_statements(self, ts_code=None):
        """Update income statements for specific ticker or all tickers"""
        try:
            if ts_code:
                # Update specific ticker
                tickers = self.session.query(Ticker).filter_by(ts_code=ts_code).all()
            else:
                # Update all tickers
                tickers = self.session.query(Ticker).all()
            
            total_updated_count = 0
            
            for i, ticker in enumerate(tickers, 1):
                try:
                    print(f"📋 Processing income statement {i}/{len(tickers)}: {ticker.ts_code} - {ticker.name}...")
                    
                    # Get income statement data from Tushare
                    income_statement_data = self.tushare_service.get_income_statement(ticker.ts_code)
                    
                    if income_statement_data:
                        # Clear existing income statements for this ticker
                        self.session.query(IncomeStatement).filter_by(ts_code=ticker.ts_code).delete()
                        
                        # Add new income statements
                        for data in income_statement_data:
                            income_statement = IncomeStatement(**data)
                            self.session.add(income_statement)
                        
                        total_updated_count += len(income_statement_data)
                        
                except Exception as ticker_error:
                    print(f"❌ Error updating income statement for {ticker.ts_code}: {ticker_error}")
                    continue
            
            self.session.commit()
            print(f"✅ Completed: Updated {total_updated_count} income statement records across {len(tickers)} tickers")
            return True, f"Updated {total_updated_count} income statement records across {len(tickers)} tickers"
            
        except Exception as e:
            self.session.rollback()
            return False, str(e)
    
    def get_financial_reports(self, ts_code, end_date=None):
        """Get financial reports (balance sheet, cash flow, income statement) for a specific ticker"""
        try:
            # Build queries with optional end_date filter
            balance_sheet_query = self.session.query(BalanceSheet).filter_by(ts_code=ts_code)
            cash_flow_query = self.session.query(CashFlow).filter_by(ts_code=ts_code)
            income_statement_query = self.session.query(IncomeStatement).filter_by(ts_code=ts_code)
            
            # Apply end_date filter if provided
            if end_date:
                balance_sheet_query = balance_sheet_query.filter(BalanceSheet.end_date == end_date)
                cash_flow_query = cash_flow_query.filter(CashFlow.end_date == end_date)
                income_statement_query = income_statement_query.filter(IncomeStatement.end_date == end_date)
            
            # Order by end_date descending
            balance_sheets = balance_sheet_query.order_by(BalanceSheet.end_date.desc()).all()
            cash_flows = cash_flow_query.order_by(CashFlow.end_date.desc()).all()
            income_statements = income_statement_query.order_by(IncomeStatement.end_date.desc()).all()
            
            # Convert to dictionaries
            balance_sheet_data = []
            for bs in balance_sheets:
                balance_sheet_data.append({
                    'ts_code': bs.ts_code,
                    'ann_date': bs.ann_date,
                    'f_ann_date': bs.f_ann_date,
                    'end_date': bs.end_date,
                    'report_type': bs.report_type,
                    'comp_type': bs.comp_type,
                    'total_share': bs.total_share,
                    'cap_rese': bs.cap_rese,
                    'undist_profit': bs.undist_profit,
                    'surplus_rese': bs.surplus_rese,
                    'special_rese': bs.special_rese,
                    'money_cap': bs.money_cap,
                    'trad_asset': bs.trad_asset,
                    'notes_receiv': bs.notes_receiv,
                    'accounts_receiv': bs.accounts_receiv,
                    'oth_receiv': bs.oth_receiv,
                    'prepayment': bs.prepayment,
                    'div_receiv': bs.div_receiv,
                    'int_receiv': bs.int_receiv,
                    'inventories': bs.inventories,
                    'amor_exp': bs.amor_exp,
                    'nca_within_1y': bs.nca_within_1y,
                    'sett_rsrv': bs.sett_rsrv,
                    'loanto_oth_bank_fi': bs.loanto_oth_bank_fi,
                    'premium_receiv': bs.premium_receiv,
                    'reinsur_receiv': bs.reinsur_receiv,
                    'reinsur_res_receiv': bs.reinsur_res_receiv,
                    'pur_resale_fa': bs.pur_resale_fa,
                    'oth_cur_assets': bs.oth_cur_assets,
                    'total_cur_assets': bs.total_cur_assets,
                    'fa_avail_for_sale': bs.fa_avail_for_sale,
                    'htm_invest': bs.htm_invest,
                    'lt_eqt_invest': bs.lt_eqt_invest,
                    'invest_real_estate': bs.invest_real_estate,
                    'time_deposits': bs.time_deposits,
                    'oth_assets': bs.oth_assets,
                    'lt_rec': bs.lt_rec,
                    'fix_assets': bs.fix_assets,
                    'cip': bs.cip,
                    'const_materials': bs.const_materials,
                    'fixed_assets_disp': bs.fixed_assets_disp,
                    'produc_bio_assets': bs.produc_bio_assets,
                    'oil_and_gas_assets': bs.oil_and_gas_assets,
                    'intan_assets': bs.intan_assets,
                    'r_and_d': bs.r_and_d,
                    'goodwill': bs.goodwill,
                    'lt_amor_exp': bs.lt_amor_exp,
                    'defer_tax_assets': bs.defer_tax_assets,
                    'decr_in_disbur': bs.decr_in_disbur,
                    'oth_nca': bs.oth_nca,
                    'total_nca': bs.total_nca,
                    'cash_reser_cb': bs.cash_reser_cb,
                    'depos_in_oth_bfi': bs.depos_in_oth_bfi,
                    'prec_metals': bs.prec_metals,
                    'deriv_assets': bs.deriv_assets,
                    'rr_reins_une_prem': bs.rr_reins_une_prem,
                    'rr_reins_outstd_cla': bs.rr_reins_outstd_cla,
                    'rr_reins_lins_liab': bs.rr_reins_lins_liab,
                    'rr_reins_lthins_liab': bs.rr_reins_lthins_liab,
                    'refund_depos': bs.refund_depos,
                    'ph_pledge_loans': bs.ph_pledge_loans,
                    'refund_cap_depos': bs.refund_cap_depos,
                    'indep_acct_assets': bs.indep_acct_assets,
                    'client_depos': bs.client_depos,
                    'client_prov': bs.client_prov,
                    'transac_seat_fee': bs.transac_seat_fee,
                    'invest_as_receiv': bs.invest_as_receiv,
                    'total_assets': bs.total_assets,
                    'lt_borr': bs.lt_borr,
                    'st_borr': bs.st_borr,
                    'cb_borr': bs.cb_borr,
                    'depos_ib_deposits': bs.depos_ib_deposits,
                    'loan_oth_bank': bs.loan_oth_bank,
                    'trading_fl': bs.trading_fl,
                    'notes_payable': bs.notes_payable,
                    'acct_payable': bs.acct_payable,
                    'adv_receipts': bs.adv_receipts,
                    'sold_for_repur_fa': bs.sold_for_repur_fa,
                    'comm_payable': bs.comm_payable,
                    'payroll_payable': bs.payroll_payable,
                    'taxes_payable': bs.taxes_payable,
                    'int_payable': bs.int_payable,
                    'div_payable': bs.div_payable,
                    'oth_payable': bs.oth_payable,
                    'acc_exp': bs.acc_exp,
                    'deferred_inc': bs.deferred_inc,
                    'st_bonds_payable': bs.st_bonds_payable,
                    'payable_to_reinsurer': bs.payable_to_reinsurer,
                    'rsrv_insur_cont': bs.rsrv_insur_cont,
                    'acting_trading_sec': bs.acting_trading_sec,
                    'acting_uw_sec': bs.acting_uw_sec,
                    'oth_cur_liab': bs.oth_cur_liab,
                    'total_cur_liab': bs.total_cur_liab,
                    'bonds_payable': bs.bonds_payable,
                    'lt_payable': bs.lt_payable,
                    'specific_payables': bs.specific_payables,
                    'estim_liab': bs.estim_liab,
                    'defer_tax_liab': bs.defer_tax_liab,
                    'defer_inc_non_cur': bs.defer_inc_non_cur,
                    'oth_ncl': bs.oth_ncl,
                    'total_ncl': bs.total_ncl,
                    'deps_proc_sell_assets': bs.deps_proc_sell_assets,
                    'reindebt_payable': bs.reindebt_payable,
                    'policy_div_payable': bs.policy_div_payable,
                    'total_liab': bs.total_liab,
                    'treasury_share': bs.treasury_share,
                    'ordin_risk_reser': bs.ordin_risk_reser,
                    'forex_differ': bs.forex_differ,
                    'invest_loss_unconf': bs.invest_loss_unconf,
                    'minority_int': bs.minority_int,
                    'total_hldr_eqy_exc_min_int': bs.total_hldr_eqy_exc_min_int,
                    'total_hldr_eqy_inc_min_int': bs.total_hldr_eqy_inc_min_int,
                    'total_liab_hldr_eqy': bs.total_liab_hldr_eqy,
                    'lt_payroll_payable': bs.lt_payroll_payable,
                    'oth_comp_income': bs.oth_comp_income,
                    'oth_eqt_tools': bs.oth_eqt_tools,
                    'oth_eqt_tools_p_shr': bs.oth_eqt_tools_p_shr,
                    'lending_funds': bs.lending_funds,
                    'acc_receivable': bs.acc_receivable,
                    'st_finl_co_borr': bs.st_finl_co_borr,
                    'deposit': bs.deposit,
                    'oth_assets_flag': bs.oth_assets_flag,
                    'update_flag': bs.update_flag,
                    'updated_date': bs.updated_date.strftime('%Y-%m-%d %H:%M:%S') if bs.updated_date else None
                })
            
            cash_flow_data = []
            for cf in cash_flows:
                cash_flow_data.append({
                    'ts_code': cf.ts_code,
                    'ann_date': cf.ann_date,
                    'f_ann_date': cf.f_ann_date,
                    'end_date': cf.end_date,
                    'report_type': cf.report_type,
                    'comp_type': cf.comp_type,
                    'net_profit': cf.net_profit,
                    'finan_exp': cf.finan_exp,
                    'c_fr_sale_sg': cf.c_fr_sale_sg,
                    'recp_tax_rends': cf.recp_tax_rends,
                    'n_depos_incr_fi': cf.n_depos_incr_fi,
                    'n_incr_loans_cb': cf.n_incr_loans_cb,
                    'n_inc_borr_oth_fi': cf.n_inc_borr_oth_fi,
                    'prem_fr_orig_contr': cf.prem_fr_orig_contr,
                    'n_incr_insured_dep': cf.n_incr_insured_dep,
                    'n_reinsur_prem': cf.n_reinsur_prem,
                    'n_incr_disp_tfa': cf.n_incr_disp_tfa,
                    'ifc_cash_incr': cf.ifc_cash_incr,
                    'n_incr_disp_faas': cf.n_incr_disp_faas,
                    'n_incr_loans_oth_bank': cf.n_incr_loans_oth_bank,
                    'n_cap_incr_repur': cf.n_cap_incr_repur,
                    'c_fr_oth_operate_a': cf.c_fr_oth_operate_a,
                    'c_inf_fr_operate_a': cf.c_inf_fr_operate_a,
                    'c_paid_goods_s': cf.c_paid_goods_s,
                    'c_paid_to_for_empl': cf.c_paid_to_for_empl,
                    'c_paid_for_taxes': cf.c_paid_for_taxes,
                    'n_incr_clt_loan_cb': cf.n_incr_clt_loan_cb,
                    'n_incr_dep_cbob': cf.n_incr_dep_cbob,
                    'c_pay_claims_orig_inco': cf.c_pay_claims_orig_inco,
                    'pay_handling_chrg': cf.pay_handling_chrg,
                    'pay_comm_insur_plcy': cf.pay_comm_insur_plcy,
                    'oth_cash_pay_oper_act': cf.oth_cash_pay_oper_act,
                    'st_cash_out_act': cf.st_cash_out_act,
                    'n_cashflow_act': cf.n_cashflow_act,
                    'oth_recp_ral_inv_act': cf.oth_recp_ral_inv_act,
                    'c_disp_withdrwl_invest': cf.c_disp_withdrwl_invest,
                    'c_recp_return_invest': cf.c_recp_return_invest,
                    'n_recp_disp_fiolta': cf.n_recp_disp_fiolta,
                    'n_recp_disp_sobu': cf.n_recp_disp_sobu,
                    'stot_inflows_inv_act': cf.stot_inflows_inv_act,
                    'c_pay_acq_const_fiolta': cf.c_pay_acq_const_fiolta,
                    'c_paid_invest': cf.c_paid_invest,
                    'n_disp_subs_oth_biz': cf.n_disp_subs_oth_biz,
                    'oth_pay_ral_inv_act': cf.oth_pay_ral_inv_act,
                    'n_incr_pledge_loan': cf.n_incr_pledge_loan,
                    'stot_out_inv_act': cf.stot_out_inv_act,
                    'n_cashflow_inv_act': cf.n_cashflow_inv_act,
                    'c_recp_borrow': cf.c_recp_borrow,
                    'proc_issue_bonds': cf.proc_issue_bonds,
                    'oth_cash_recp_ral_fnc_act': cf.oth_cash_recp_ral_fnc_act,
                    'stot_cash_in_fnc_act': cf.stot_cash_in_fnc_act,
                    'free_cashflow': cf.free_cashflow,
                    'c_prepay_amt_borr': cf.c_prepay_amt_borr,
                    'c_pay_dist_dpcp_int_exp': cf.c_pay_dist_dpcp_int_exp,
                    'incl_dvd_profit_paid_sc_ms': cf.incl_dvd_profit_paid_sc_ms,
                    'oth_cashpay_ral_fnc_act': cf.oth_cashpay_ral_fnc_act,
                    'stot_cashout_fnc_act': cf.stot_cashout_fnc_act,
                    'n_cash_flows_fnc_act': cf.n_cash_flows_fnc_act,
                    'eff_fx_flu_cash': cf.eff_fx_flu_cash,
                    'n_incr_cash_cash_equ': cf.n_incr_cash_cash_equ,
                    'c_cash_equ_beg_period': cf.c_cash_equ_beg_period,
                    'c_cash_equ_end_period': cf.c_cash_equ_end_period,
                    'c_recp_cap_contrib': cf.c_recp_cap_contrib,
                    'incl_cash_rec_sg': cf.incl_cash_rec_sg,
                    'uncon_invest_loss': cf.uncon_invest_loss,
                    'prov_depr_assets': cf.prov_depr_assets,
                    'depr_fa_coga_dpba': cf.depr_fa_coga_dpba,
                    'amort_intang_assets': cf.amort_intang_assets,
                    'lt_amort_deferred_exp': cf.lt_amort_deferred_exp,
                    'decr_deferred_exp': cf.decr_deferred_exp,
                    'incr_acc_exp': cf.incr_acc_exp,
                    'loss_disp_fiolta': cf.loss_disp_fiolta,
                    'loss_scr_fa': cf.loss_scr_fa,
                    'loss_fv_chg': cf.loss_fv_chg,
                    'invest_loss': cf.invest_loss,
                    'decr_def_inc_tax_assets': cf.decr_def_inc_tax_assets,
                    'incr_def_inc_tax_liab': cf.incr_def_inc_tax_liab,
                    'decr_inventories': cf.decr_inventories,
                    'decr_oper_payable': cf.decr_oper_payable,
                    'incr_oper_payable': cf.incr_oper_payable,
                    'others': cf.others,
                    'im_net_cashflow_oper_act': cf.im_net_cashflow_oper_act,
                    'conv_debt_into_cap': cf.conv_debt_into_cap,
                    'conv_copbonds_due_within_1y': cf.conv_copbonds_due_within_1y,
                    'fa_fnc_leases': cf.fa_fnc_leases,
                    'im_n_incr_cash_equ': cf.im_n_incr_cash_equ,
                    'net_dism_capital_add': cf.net_dism_capital_add,
                    'net_cash_rece_sec': cf.net_cash_rece_sec,
                    'credit_impa_loss': cf.credit_impa_loss,
                    'use_sett_prov': cf.use_sett_prov,
                    'oth_loss_assets': cf.oth_loss_assets,
                    'end_bal_cash': cf.end_bal_cash,
                    'beg_bal_cash': cf.beg_bal_cash,
                    'end_bal_cash_equ': cf.end_bal_cash_equ,
                    'beg_bal_cash_equ': cf.beg_bal_cash_equ,
                    'update_flag': cf.update_flag,
                    'updated_date': cf.updated_date.strftime('%Y-%m-%d %H:%M:%S') if cf.updated_date else None
                })
            
            income_statement_data = []
            for is_item in income_statements:
                income_statement_data.append({
                    'ts_code': is_item.ts_code,
                    'ann_date': is_item.ann_date,
                    'f_ann_date': is_item.f_ann_date,
                    'end_date': is_item.end_date,
                    'report_type': is_item.report_type,
                    'comp_type': is_item.comp_type,
                    'basic_eps': is_item.basic_eps,
                    'diluted_eps': is_item.diluted_eps,
                    'total_revenue': is_item.total_revenue,
                    'revenue': is_item.revenue,
                    'int_income': is_item.int_income,
                    'prem_earned': is_item.prem_earned,
                    'comm_income': is_item.comm_income,
                    'n_commis_income': is_item.n_commis_income,
                    'n_oth_income': is_item.n_oth_income,
                    'n_oth_biz_income': is_item.n_oth_biz_income,
                    'prem_income': is_item.prem_income,
                    'out_prem': is_item.out_prem,
                    'une_prem_reser': is_item.une_prem_reser,
                    'reins_income': is_item.reins_income,
                    'n_sec_tb_income': is_item.n_sec_tb_income,
                    'n_undwrt_sec_income': is_item.n_undwrt_sec_income,
                    'n_indemnity_reser': is_item.n_indemnity_reser,
                    'n_ins_rsrv_rec': is_item.n_ins_rsrv_rec,
                    'n_disp_tfa': is_item.n_disp_tfa,
                    'n_disp_faas': is_item.n_disp_faas,
                    'n_disp_oth_assets': is_item.n_disp_oth_assets,
                    'n_disp_oth_fa': is_item.n_disp_oth_fa,
                    'n_disp_fiolta': is_item.n_disp_fiolta,
                    'n_disp_cip': is_item.n_disp_cip,
                    'n_disp_bio_assets': is_item.n_disp_bio_assets,
                    'n_disp_mi': is_item.n_disp_mi,
                    'n_disp_oth_nca': is_item.n_disp_oth_nca,
                    'n_disp_subs_oth_biz': is_item.n_disp_subs_oth_biz,
                    'n_oth_fa': is_item.n_oth_fa,
                    'n_disp_oth_biz': is_item.n_disp_oth_biz,
                    'n_oth_comp_income': is_item.n_oth_comp_income,
                    'n_oth_comp_income_attr_p': is_item.n_oth_comp_income_attr_p,
                    'n_oth_comp_income_attr_m_s': is_item.n_oth_comp_income_attr_m_s,
                    'n_oth_comp_income_atsopc': is_item.n_oth_comp_income_atsopc,
                    'n_oth_comp_income_attr_m_s_atsopc': is_item.n_oth_comp_income_attr_m_s_atsopc,
                    'n_oth_comp_income_atsop': is_item.n_oth_comp_income_atsop,
                    'n_income_attr_p': is_item.n_income_attr_p,
                    'n_income_attr_m_s': is_item.n_income_attr_m_s,
                    'n_income_discontinued': is_item.n_income_discontinued,
                    'n_income_attr_p_discontinued': is_item.n_income_attr_p_discontinued,
                    'n_income_attr_m_s_discontinued': is_item.n_income_attr_m_s_discontinued,
                    'n_income_attr_p_ci': is_item.n_income_attr_p_ci,
                    'n_income_attr_m_s_ci': is_item.n_income_attr_m_s_ci,
                    'n_income': is_item.n_income,
                    'n_income_bef_na': is_item.n_income_bef_na,
                    'n_income_bef_na_attr_p': is_item.n_income_bef_na_attr_p,
                    'n_income_bef_na_attr_m_s': is_item.n_income_bef_na_attr_m_s,
                    'n_income_bef_na_discontinued': is_item.n_income_bef_na_discontinued,
                    'n_income_bef_na_attr_p_discontinued': is_item.n_income_bef_na_attr_p_discontinued,
                    'n_income_bef_na_attr_m_s_discontinued': is_item.n_income_bef_na_attr_m_s_discontinued,
                    'n_income_bef_na_attr_p_ci': is_item.n_income_bef_na_attr_p_ci,
                    'n_income_bef_na_attr_m_s_ci': is_item.n_income_bef_na_attr_m_s_ci,
                    'n_income_bef_na_atsopc': is_item.n_income_bef_na_atsopc,
                    'n_income_bef_na_attr_p_atsopc': is_item.n_income_bef_na_attr_p_atsopc,
                    'n_income_bef_na_attr_m_s_atsopc': is_item.n_income_bef_na_attr_m_s_atsopc,
                    'n_income_bef_na_discontinued_atsopc': is_item.n_income_bef_na_discontinued_atsopc,
                    'n_income_bef_na_attr_p_discontinued_atsopc': is_item.n_income_bef_na_attr_p_discontinued_atsopc,
                    'n_income_bef_na_attr_m_s_discontinued_atsopc': is_item.n_income_bef_na_attr_m_s_discontinued_atsopc,
                    'n_income_bef_na_attr_p_ci_atsopc': is_item.n_income_bef_na_attr_p_ci_atsopc,
                    'n_income_bef_na_attr_m_s_ci_atsopc': is_item.n_income_bef_na_attr_m_s_ci_atsopc,
                    'net_profit': is_item.net_profit,
                    'net_profit_attr_p': is_item.net_profit_attr_p,
                    'net_profit_attr_m_s': is_item.net_profit_attr_m_s,
                    'net_profit_discontinued': is_item.net_profit_discontinued,
                    'net_profit_attr_p_discontinued': is_item.net_profit_attr_p_discontinued,
                    'net_profit_attr_m_s_discontinued': is_item.net_profit_attr_m_s_discontinued,
                    'net_profit_attr_p_ci': is_item.net_profit_attr_p_ci,
                    'net_profit_attr_m_s_ci': is_item.net_profit_attr_m_s_ci,
                    'net_profit_atsopc': is_item.net_profit_atsopc,
                    'net_profit_attr_p_atsopc': is_item.net_profit_attr_p_atsopc,
                    'net_profit_attr_m_s_atsopc': is_item.net_profit_attr_m_s_atsopc,
                    'net_profit_discontinued_atsopc': is_item.net_profit_discontinued_atsopc,
                    'net_profit_attr_p_discontinued_atsopc': is_item.net_profit_attr_p_discontinued_atsopc,
                    'net_profit_attr_m_s_discontinued_atsopc': is_item.net_profit_attr_m_s_discontinued_atsopc,
                    'net_profit_attr_p_ci_atsopc': is_item.net_profit_attr_p_ci_atsopc,
                    'net_profit_attr_m_s_ci_atsopc': is_item.net_profit_attr_m_s_ci_atsopc,
                    'update_flag': is_item.update_flag,
                    'updated_date': is_item.updated_date.strftime('%Y-%m-%d %H:%M:%S') if is_item.updated_date else None
                })
            
            return {
                'balance_sheets': balance_sheet_data,
                'cash_flows': cash_flow_data,
                'income_statements': income_statement_data
            }
            
        except Exception as e:
            print(f"Error fetching financial reports for {ts_code}: {e}")
            return None

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
