import os
import tushare as ts
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
load_dotenv()

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

    def get_hm_list(self, name='', fields=''):
        """
        Get hm_list data from Tushare
        Reference: https://tushare.pro/document/2?doc_id=311
        """
        try:
            # Get hm_list data
            df = self.pro.hm_list(
                name=name,
                fields=fields if fields else 'name,desc,orgs'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            hm_list_data = []
            for _, row in df.iterrows():
                hm_list_data.append({
                    'name': row['name'],
                    'desc': row['desc'] if 'desc' in row else '',
                    'orgs': row['orgs'] if 'orgs' in row else ''
                })
            
            return hm_list_data
            
        except Exception as e:
            print(f"Error fetching hm_list: {e}")
            return []

    def get_hm_detail(self, name='', start_date='', end_date='', fields=''):
        """
        Get hm_detail data from Tushare
        Reference: https://tushare.pro/document/2?doc_id=312
        """
        try:
            # Get hm_detail data
            df = self.pro.hm_detail(
                name=name,
                start_date=start_date,
                end_date=end_date,
                fields=fields if fields else 'trade_date,ts_code,ts_name,buy_amount,sell_amount,hm_name,hm_orgs,net_amount'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            hm_detail_data = []
            for _, row in df.iterrows():
                hm_detail_data.append({
                    'trade_date': str(row['trade_date']) if pd.notna(row['trade_date']) else '',
                    'ts_code': row['ts_code'] if 'ts_code' in row else '',
                    'ts_name': row['ts_name'] if 'ts_name' in row else '',
                    'buy_amount': float(row['buy_amount']) if pd.notna(row.get('buy_amount')) else 0.0,
                    'sell_amount': float(row['sell_amount']) if pd.notna(row.get('sell_amount')) else 0.0,
                    'name': row['hm_name'] if 'hm_name' in row else '',
                    'orgs': row['hm_orgs'] if 'hm_orgs' in row else '',
                    'net_amount': float(row['net_amount']) if pd.notna(row.get('net_amount')) else 0.0
                })
            
            return hm_detail_data
            
        except Exception as e:
            print(f"Error fetching hm_detail: {e}")
            return []

    def get_balance_sheet(self, ts_code, start_date='', end_date='', fields=''):
        """
        Get balance sheet data from Tushare
        Reference: https://tushare.pro/document/2?doc_id=220
        """
        try:
            # Get balance sheet data
            df = self.pro.balancesheet(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields if fields else 'ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_share,cap_rese,undist_profit,surplus_rese,special_rese,money_cap,trad_asset,notes_receiv,accounts_receiv,oth_receiv,prepayment,div_receiv,int_receiv,inventories,amor_exp,nca_within_1y,sett_rsrv,loanto_oth_bank_fi,premium_receiv,reinsur_receiv,reinsur_res_receiv,pur_resale_fa,oth_cur_assets,total_cur_assets,fa_avail_for_sale,htm_invest,lt_eqt_invest,invest_real_estate,time_deposits,oth_assets,lt_rec,fix_assets,cip,const_materials,fixed_assets_disp,produc_bio_assets,oil_and_gas_assets,intan_assets,r_and_d,goodwill,lt_amor_exp,defer_tax_assets,decr_in_disbur,oth_nca,total_nca,cash_reser_cb,depos_in_oth_bfi,prec_metals,deriv_assets,rr_reins_une_prem,rr_reins_outstd_cla,rr_reins_lins_liab,rr_reins_lthins_liab,refund_depos,ph_pledge_loans,refund_cap_depos,indep_acct_assets,client_depos,client_prov,transac_seat_fee,invest_as_receiv,total_assets,lt_borr,st_borr,cb_borr,depos_ib_deposits,loan_oth_bank,trading_fl,notes_payable,acct_payable,adv_receipts,sold_for_repur_fa,comm_payable,payroll_payable,taxes_payable,int_payable,div_payable,oth_payable,acc_exp,deferred_inc,st_bonds_payable,payable_to_reinsurer,rsrv_insur_cont,acting_trading_sec,acting_uw_sec,oth_cur_liab,total_cur_liab,bonds_payable,lt_payable,specific_payables,estim_liab,defer_tax_liab,defer_inc_non_cur,oth_ncl,total_ncl,deps_proc_sell_assets,reindebt_payable,policy_div_payable,total_liab,treasury_share,ordin_risk_reser,forex_differ,invest_loss_unconf,minority_int,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,total_liab_hldr_eqy,lt_payroll_payable,oth_comp_income,oth_eqt_tools,oth_eqt_tools_p_shr,lending_funds,acc_receivable,st_finl_co_borr,deposit,oth_assets_flag,update_flag'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            balance_sheet_data = []
            for _, row in df.iterrows():
                balance_sheet_data.append({
                    'ts_code': row['ts_code'] if 'ts_code' in row else '',
                    'ann_date': str(row['ann_date']) if pd.notna(row.get('ann_date')) else '',
                    'f_ann_date': str(row['f_ann_date']) if pd.notna(row.get('f_ann_date')) else '',
                    'end_date': str(row['end_date']) if pd.notna(row.get('end_date')) else '',
                    'report_type': row['report_type'] if 'report_type' in row else '',
                    'comp_type': row['comp_type'] if 'comp_type' in row else '',
                    'total_share': float(row['total_share']) if pd.notna(row.get('total_share')) else 0.0,
                    'cap_rese': float(row['cap_rese']) if pd.notna(row.get('cap_rese')) else 0.0,
                    'undist_profit': float(row['undist_profit']) if pd.notna(row.get('undist_profit')) else 0.0,
                    'surplus_rese': float(row['surplus_rese']) if pd.notna(row.get('surplus_rese')) else 0.0,
                    'special_rese': float(row['special_rese']) if pd.notna(row.get('special_rese')) else 0.0,
                    'money_cap': float(row['money_cap']) if pd.notna(row.get('money_cap')) else 0.0,
                    'trad_asset': float(row['trad_asset']) if pd.notna(row.get('trad_asset')) else 0.0,
                    'notes_receiv': float(row['notes_receiv']) if pd.notna(row.get('notes_receiv')) else 0.0,
                    'accounts_receiv': float(row['accounts_receiv']) if pd.notna(row.get('accounts_receiv')) else 0.0,
                    'oth_receiv': float(row['oth_receiv']) if pd.notna(row.get('oth_receiv')) else 0.0,
                    'prepayment': float(row['prepayment']) if pd.notna(row.get('prepayment')) else 0.0,
                    'div_receiv': float(row['div_receiv']) if pd.notna(row.get('div_receiv')) else 0.0,
                    'int_receiv': float(row['int_receiv']) if pd.notna(row.get('int_receiv')) else 0.0,
                    'inventories': float(row['inventories']) if pd.notna(row.get('inventories')) else 0.0,
                    'amor_exp': float(row['amor_exp']) if pd.notna(row.get('amor_exp')) else 0.0,
                    'nca_within_1y': float(row['nca_within_1y']) if pd.notna(row.get('nca_within_1y')) else 0.0,
                    'sett_rsrv': float(row['sett_rsrv']) if pd.notna(row.get('sett_rsrv')) else 0.0,
                    'loanto_oth_bank_fi': float(row['loanto_oth_bank_fi']) if pd.notna(row.get('loanto_oth_bank_fi')) else 0.0,
                    'premium_receiv': float(row['premium_receiv']) if pd.notna(row.get('premium_receiv')) else 0.0,
                    'reinsur_receiv': float(row['reinsur_receiv']) if pd.notna(row.get('reinsur_receiv')) else 0.0,
                    'reinsur_res_receiv': float(row['reinsur_res_receiv']) if pd.notna(row.get('reinsur_res_receiv')) else 0.0,
                    'pur_resale_fa': float(row['pur_resale_fa']) if pd.notna(row.get('pur_resale_fa')) else 0.0,
                    'oth_cur_assets': float(row['oth_cur_assets']) if pd.notna(row.get('oth_cur_assets')) else 0.0,
                    'total_cur_assets': float(row['total_cur_assets']) if pd.notna(row.get('total_cur_assets')) else 0.0,
                    'fa_avail_for_sale': float(row['fa_avail_for_sale']) if pd.notna(row.get('fa_avail_for_sale')) else 0.0,
                    'htm_invest': float(row['htm_invest']) if pd.notna(row.get('htm_invest')) else 0.0,
                    'lt_eqt_invest': float(row['lt_eqt_invest']) if pd.notna(row.get('lt_eqt_invest')) else 0.0,
                    'invest_real_estate': float(row['invest_real_estate']) if pd.notna(row.get('invest_real_estate')) else 0.0,
                    'time_deposits': float(row['time_deposits']) if pd.notna(row.get('time_deposits')) else 0.0,
                    'oth_assets': float(row['oth_assets']) if pd.notna(row.get('oth_assets')) else 0.0,
                    'lt_rec': float(row['lt_rec']) if pd.notna(row.get('lt_rec')) else 0.0,
                    'fix_assets': float(row['fix_assets']) if pd.notna(row.get('fix_assets')) else 0.0,
                    'cip': float(row['cip']) if pd.notna(row.get('cip')) else 0.0,
                    'const_materials': float(row['const_materials']) if pd.notna(row.get('const_materials')) else 0.0,
                    'fixed_assets_disp': float(row['fixed_assets_disp']) if pd.notna(row.get('fixed_assets_disp')) else 0.0,
                    'produc_bio_assets': float(row['produc_bio_assets']) if pd.notna(row.get('produc_bio_assets')) else 0.0,
                    'oil_and_gas_assets': float(row['oil_and_gas_assets']) if pd.notna(row.get('oil_and_gas_assets')) else 0.0,
                    'intan_assets': float(row['intan_assets']) if pd.notna(row.get('intan_assets')) else 0.0,
                    'r_and_d': float(row['r_and_d']) if pd.notna(row.get('r_and_d')) else 0.0,
                    'goodwill': float(row['goodwill']) if pd.notna(row.get('goodwill')) else 0.0,
                    'lt_amor_exp': float(row['lt_amor_exp']) if pd.notna(row.get('lt_amor_exp')) else 0.0,
                    'defer_tax_assets': float(row['defer_tax_assets']) if pd.notna(row.get('defer_tax_assets')) else 0.0,
                    'decr_in_disbur': float(row['decr_in_disbur']) if pd.notna(row.get('decr_in_disbur')) else 0.0,
                    'oth_nca': float(row['oth_nca']) if pd.notna(row.get('oth_nca')) else 0.0,
                    'total_nca': float(row['total_nca']) if pd.notna(row.get('total_nca')) else 0.0,
                    'cash_reser_cb': float(row['cash_reser_cb']) if pd.notna(row.get('cash_reser_cb')) else 0.0,
                    'depos_in_oth_bfi': float(row['depos_in_oth_bfi']) if pd.notna(row.get('depos_in_oth_bfi')) else 0.0,
                    'prec_metals': float(row['prec_metals']) if pd.notna(row.get('prec_metals')) else 0.0,
                    'deriv_assets': float(row['deriv_assets']) if pd.notna(row.get('deriv_assets')) else 0.0,
                    'rr_reins_une_prem': float(row['rr_reins_une_prem']) if pd.notna(row.get('rr_reins_une_prem')) else 0.0,
                    'rr_reins_outstd_cla': float(row['rr_reins_outstd_cla']) if pd.notna(row.get('rr_reins_outstd_cla')) else 0.0,
                    'rr_reins_lins_liab': float(row['rr_reins_lins_liab']) if pd.notna(row.get('rr_reins_lins_liab')) else 0.0,
                    'rr_reins_lthins_liab': float(row['rr_reins_lthins_liab']) if pd.notna(row.get('rr_reins_lthins_liab')) else 0.0,
                    'refund_depos': float(row['refund_depos']) if pd.notna(row.get('refund_depos')) else 0.0,
                    'ph_pledge_loans': float(row['ph_pledge_loans']) if pd.notna(row.get('ph_pledge_loans')) else 0.0,
                    'refund_cap_depos': float(row['refund_cap_depos']) if pd.notna(row.get('refund_cap_depos')) else 0.0,
                    'indep_acct_assets': float(row['indep_acct_assets']) if pd.notna(row.get('indep_acct_assets')) else 0.0,
                    'client_depos': float(row['client_depos']) if pd.notna(row.get('client_depos')) else 0.0,
                    'client_prov': float(row['client_prov']) if pd.notna(row.get('client_prov')) else 0.0,
                    'transac_seat_fee': float(row['transac_seat_fee']) if pd.notna(row.get('transac_seat_fee')) else 0.0,
                    'invest_as_receiv': float(row['invest_as_receiv']) if pd.notna(row.get('invest_as_receiv')) else 0.0,
                    'total_assets': float(row['total_assets']) if pd.notna(row.get('total_assets')) else 0.0,
                    'lt_borr': float(row['lt_borr']) if pd.notna(row.get('lt_borr')) else 0.0,
                    'st_borr': float(row['st_borr']) if pd.notna(row.get('st_borr')) else 0.0,
                    'cb_borr': float(row['cb_borr']) if pd.notna(row.get('cb_borr')) else 0.0,
                    'depos_ib_deposits': float(row['depos_ib_deposits']) if pd.notna(row.get('depos_ib_deposits')) else 0.0,
                    'loan_oth_bank': float(row['loan_oth_bank']) if pd.notna(row.get('loan_oth_bank')) else 0.0,
                    'trading_fl': float(row['trading_fl']) if pd.notna(row.get('trading_fl')) else 0.0,
                    'notes_payable': float(row['notes_payable']) if pd.notna(row.get('notes_payable')) else 0.0,
                    'acct_payable': float(row['acct_payable']) if pd.notna(row.get('acct_payable')) else 0.0,
                    'adv_receipts': float(row['adv_receipts']) if pd.notna(row.get('adv_receipts')) else 0.0,
                    'sold_for_repur_fa': float(row['sold_for_repur_fa']) if pd.notna(row.get('sold_for_repur_fa')) else 0.0,
                    'comm_payable': float(row['comm_payable']) if pd.notna(row.get('comm_payable')) else 0.0,
                    'payroll_payable': float(row['payroll_payable']) if pd.notna(row.get('payroll_payable')) else 0.0,
                    'taxes_payable': float(row['taxes_payable']) if pd.notna(row.get('taxes_payable')) else 0.0,
                    'int_payable': float(row['int_payable']) if pd.notna(row.get('int_payable')) else 0.0,
                    'div_payable': float(row['div_payable']) if pd.notna(row.get('div_payable')) else 0.0,
                    'oth_payable': float(row['oth_payable']) if pd.notna(row.get('oth_payable')) else 0.0,
                    'acc_exp': float(row['acc_exp']) if pd.notna(row.get('acc_exp')) else 0.0,
                    'deferred_inc': float(row['deferred_inc']) if pd.notna(row.get('deferred_inc')) else 0.0,
                    'st_bonds_payable': float(row['st_bonds_payable']) if pd.notna(row.get('st_bonds_payable')) else 0.0,
                    'payable_to_reinsurer': float(row['payable_to_reinsurer']) if pd.notna(row.get('payable_to_reinsurer')) else 0.0,
                    'rsrv_insur_cont': float(row['rsrv_insur_cont']) if pd.notna(row.get('rsrv_insur_cont')) else 0.0,
                    'acting_trading_sec': float(row['acting_trading_sec']) if pd.notna(row.get('acting_trading_sec')) else 0.0,
                    'acting_uw_sec': float(row['acting_uw_sec']) if pd.notna(row.get('acting_uw_sec')) else 0.0,
                    'oth_cur_liab': float(row['oth_cur_liab']) if pd.notna(row.get('oth_cur_liab')) else 0.0,
                    'total_cur_liab': float(row['total_cur_liab']) if pd.notna(row.get('total_cur_liab')) else 0.0,
                    'bonds_payable': float(row['bonds_payable']) if pd.notna(row.get('bonds_payable')) else 0.0,
                    'lt_payable': float(row['lt_payable']) if pd.notna(row.get('lt_payable')) else 0.0,
                    'specific_payables': float(row['specific_payables']) if pd.notna(row.get('specific_payables')) else 0.0,
                    'estim_liab': float(row['estim_liab']) if pd.notna(row.get('estim_liab')) else 0.0,
                    'defer_tax_liab': float(row['defer_tax_liab']) if pd.notna(row.get('defer_tax_liab')) else 0.0,
                    'defer_inc_non_cur': float(row['defer_inc_non_cur']) if pd.notna(row.get('defer_inc_non_cur')) else 0.0,
                    'oth_ncl': float(row['oth_ncl']) if pd.notna(row.get('oth_ncl')) else 0.0,
                    'total_ncl': float(row['total_ncl']) if pd.notna(row.get('total_ncl')) else 0.0,
                    'deps_proc_sell_assets': float(row['deps_proc_sell_assets']) if pd.notna(row.get('deps_proc_sell_assets')) else 0.0,
                    'reindebt_payable': float(row['reindebt_payable']) if pd.notna(row.get('reindebt_payable')) else 0.0,
                    'policy_div_payable': float(row['policy_div_payable']) if pd.notna(row.get('policy_div_payable')) else 0.0,
                    'total_liab': float(row['total_liab']) if pd.notna(row.get('total_liab')) else 0.0,
                    'treasury_share': float(row['treasury_share']) if pd.notna(row.get('treasury_share')) else 0.0,
                    'ordin_risk_reser': float(row['ordin_risk_reser']) if pd.notna(row.get('ordin_risk_reser')) else 0.0,
                    'forex_differ': float(row['forex_differ']) if pd.notna(row.get('forex_differ')) else 0.0,
                    'invest_loss_unconf': float(row['invest_loss_unconf']) if pd.notna(row.get('invest_loss_unconf')) else 0.0,
                    'minority_int': float(row['minority_int']) if pd.notna(row.get('minority_int')) else 0.0,
                    'total_hldr_eqy_exc_min_int': float(row['total_hldr_eqy_exc_min_int']) if pd.notna(row.get('total_hldr_eqy_exc_min_int')) else 0.0,
                    'total_hldr_eqy_inc_min_int': float(row['total_hldr_eqy_inc_min_int']) if pd.notna(row.get('total_hldr_eqy_inc_min_int')) else 0.0,
                    'total_liab_hldr_eqy': float(row['total_liab_hldr_eqy']) if pd.notna(row.get('total_liab_hldr_eqy')) else 0.0,
                    'lt_payroll_payable': float(row['lt_payroll_payable']) if pd.notna(row.get('lt_payroll_payable')) else 0.0,
                    'oth_comp_income': float(row['oth_comp_income']) if pd.notna(row.get('oth_comp_income')) else 0.0,
                    'oth_eqt_tools': float(row['oth_eqt_tools']) if pd.notna(row.get('oth_eqt_tools')) else 0.0,
                    'oth_eqt_tools_p_shr': float(row['oth_eqt_tools_p_shr']) if pd.notna(row.get('oth_eqt_tools_p_shr')) else 0.0,
                    'lending_funds': float(row['lending_funds']) if pd.notna(row.get('lending_funds')) else 0.0,
                    'acc_receivable': float(row['acc_receivable']) if pd.notna(row.get('acc_receivable')) else 0.0,
                    'st_finl_co_borr': float(row['st_finl_co_borr']) if pd.notna(row.get('st_finl_co_borr')) else 0.0,
                    'deposit': float(row['deposit']) if pd.notna(row.get('deposit')) else 0.0,
                    'oth_assets_flag': float(row['oth_assets_flag']) if pd.notna(row.get('oth_assets_flag')) else 0.0,
                    'update_flag': float(row['update_flag']) if pd.notna(row.get('update_flag')) else 0.0
                })
            
            return balance_sheet_data
            
        except Exception as e:
            print(f"Error fetching balance sheet for {ts_code}: {e}")
            return []

    def get_cash_flow(self, ts_code, start_date='', end_date='', fields=''):
        """
        Get cash flow data from Tushare
        Reference: https://tushare.pro/document/2?doc_id=221
        """
        try:
            # Get cash flow data
            df = self.pro.cashflow(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields if fields else 'ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,net_profit,finan_exp,c_fr_sale_sg,recp_tax_rends,n_depos_incr_fi,n_incr_loans_cb,n_inc_borr_oth_fi,prem_fr_orig_contr,n_incr_insured_dep,n_reinsur_prem,n_incr_disp_tfa,ifc_cash_incr,n_incr_disp_faas,n_incr_loans_oth_bank,n_cap_incr_repur,c_fr_oth_operate_a,c_inf_fr_operate_a,c_paid_goods_s,c_paid_to_for_empl,c_paid_for_taxes,n_incr_clt_loan_cb,n_incr_dep_cbob,c_pay_claims_orig_inco,pay_handling_chrg,pay_comm_insur_plcy,oth_cash_pay_oper_act,st_cash_out_act,n_cashflow_act,oth_recp_ral_inv_act,c_disp_withdrwl_invest,c_recp_return_invest,n_recp_disp_fiolta,n_recp_disp_sobu,stot_inflows_inv_act,c_pay_acq_const_fiolta,c_paid_invest,n_disp_subs_oth_biz,oth_pay_ral_inv_act,n_incr_pledge_loan,stot_out_inv_act,n_cashflow_inv_act,c_recp_borrow,proc_issue_bonds,oth_cash_recp_ral_fnc_act,stot_cash_in_fnc_act,free_cashflow,c_prepay_amt_borr,c_pay_dist_dpcp_int_exp,incl_dvd_profit_paid_sc_ms,oth_cashpay_ral_fnc_act,stot_cashout_fnc_act,n_cash_flows_fnc_act,eff_fx_flu_cash,n_incr_cash_cash_equ,c_cash_equ_beg_period,c_cash_equ_end_period,c_recp_cap_contrib,incl_cash_rec_sg,uncon_invest_loss,prov_depr_assets,depr_fa_coga_dpba,amort_intang_assets,lt_amort_deferred_exp,decr_deferred_exp,incr_acc_exp,loss_disp_fiolta,loss_scr_fa,loss_fv_chg,invest_loss,decr_def_inc_tax_assets,incr_def_inc_tax_liab,decr_inventories,decr_oper_payable,incr_oper_payable,others,im_net_cashflow_oper_act,conv_debt_into_cap,conv_copbonds_due_within_1y,fa_fnc_leases,im_n_incr_cash_equ,net_dism_capital_add,net_cash_rece_sec,credit_impa_loss,use_sett_prov,oth_loss_assets,end_bal_cash,beg_bal_cash,end_bal_cash_equ,beg_bal_cash_equ,update_flag'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            cash_flow_data = []
            for _, row in df.iterrows():
                cash_flow_data.append({
                    'ts_code': row['ts_code'] if 'ts_code' in row else '',
                    'ann_date': str(row['ann_date']) if pd.notna(row.get('ann_date')) else '',
                    'f_ann_date': str(row['f_ann_date']) if pd.notna(row.get('f_ann_date')) else '',
                    'end_date': str(row['end_date']) if pd.notna(row.get('end_date')) else '',
                    'report_type': row['report_type'] if 'report_type' in row else '',
                    'comp_type': row['comp_type'] if 'comp_type' in row else '',
                    'net_profit': float(row['net_profit']) if pd.notna(row.get('net_profit')) else 0.0,
                    'finan_exp': float(row['finan_exp']) if pd.notna(row.get('finan_exp')) else 0.0,
                    'c_fr_sale_sg': float(row['c_fr_sale_sg']) if pd.notna(row.get('c_fr_sale_sg')) else 0.0,
                    'recp_tax_rends': float(row['recp_tax_rends']) if pd.notna(row.get('recp_tax_rends')) else 0.0,
                    'n_depos_incr_fi': float(row['n_depos_incr_fi']) if pd.notna(row.get('n_depos_incr_fi')) else 0.0,
                    'n_incr_loans_cb': float(row['n_incr_loans_cb']) if pd.notna(row.get('n_incr_loans_cb')) else 0.0,
                    'n_inc_borr_oth_fi': float(row['n_inc_borr_oth_fi']) if pd.notna(row.get('n_inc_borr_oth_fi')) else 0.0,
                    'prem_fr_orig_contr': float(row['prem_fr_orig_contr']) if pd.notna(row.get('prem_fr_orig_contr')) else 0.0,
                    'n_incr_insured_dep': float(row['n_incr_insured_dep']) if pd.notna(row.get('n_incr_insured_dep')) else 0.0,
                    'n_reinsur_prem': float(row['n_reinsur_prem']) if pd.notna(row.get('n_reinsur_prem')) else 0.0,
                    'n_incr_disp_tfa': float(row['n_incr_disp_tfa']) if pd.notna(row.get('n_incr_disp_tfa')) else 0.0,
                    'ifc_cash_incr': float(row['ifc_cash_incr']) if pd.notna(row.get('ifc_cash_incr')) else 0.0,
                    'n_incr_disp_faas': float(row['n_incr_disp_faas']) if pd.notna(row.get('n_incr_disp_faas')) else 0.0,
                    'n_incr_loans_oth_bank': float(row['n_incr_loans_oth_bank']) if pd.notna(row.get('n_incr_loans_oth_bank')) else 0.0,
                    'n_cap_incr_repur': float(row['n_cap_incr_repur']) if pd.notna(row.get('n_cap_incr_repur')) else 0.0,
                    'c_fr_oth_operate_a': float(row['c_fr_oth_operate_a']) if pd.notna(row.get('c_fr_oth_operate_a')) else 0.0,
                    'c_inf_fr_operate_a': float(row['c_inf_fr_operate_a']) if pd.notna(row.get('c_inf_fr_operate_a')) else 0.0,
                    'c_paid_goods_s': float(row['c_paid_goods_s']) if pd.notna(row.get('c_paid_goods_s')) else 0.0,
                    'c_paid_to_for_empl': float(row['c_paid_to_for_empl']) if pd.notna(row.get('c_paid_to_for_empl')) else 0.0,
                    'c_paid_for_taxes': float(row['c_paid_for_taxes']) if pd.notna(row.get('c_paid_for_taxes')) else 0.0,
                    'n_incr_clt_loan_cb': float(row['n_incr_clt_loan_cb']) if pd.notna(row.get('n_incr_clt_loan_cb')) else 0.0,
                    'n_incr_dep_cbob': float(row['n_incr_dep_cbob']) if pd.notna(row.get('n_incr_dep_cbob')) else 0.0,
                    'c_pay_claims_orig_inco': float(row['c_pay_claims_orig_inco']) if pd.notna(row.get('c_pay_claims_orig_inco')) else 0.0,
                    'pay_handling_chrg': float(row['pay_handling_chrg']) if pd.notna(row.get('pay_handling_chrg')) else 0.0,
                    'pay_comm_insur_plcy': float(row['pay_comm_insur_plcy']) if pd.notna(row.get('pay_comm_insur_plcy')) else 0.0,
                    'oth_cash_pay_oper_act': float(row['oth_cash_pay_oper_act']) if pd.notna(row.get('oth_cash_pay_oper_act')) else 0.0,
                    'st_cash_out_act': float(row['st_cash_out_act']) if pd.notna(row.get('st_cash_out_act')) else 0.0,
                    'n_cashflow_act': float(row['n_cashflow_act']) if pd.notna(row.get('n_cashflow_act')) else 0.0,
                    'oth_recp_ral_inv_act': float(row['oth_recp_ral_inv_act']) if pd.notna(row.get('oth_recp_ral_inv_act')) else 0.0,
                    'c_disp_withdrwl_invest': float(row['c_disp_withdrwl_invest']) if pd.notna(row.get('c_disp_withdrwl_invest')) else 0.0,
                    'c_recp_return_invest': float(row['c_recp_return_invest']) if pd.notna(row.get('c_recp_return_invest')) else 0.0,
                    'n_recp_disp_fiolta': float(row['n_recp_disp_fiolta']) if pd.notna(row.get('n_recp_disp_fiolta')) else 0.0,
                    'n_recp_disp_sobu': float(row['n_recp_disp_sobu']) if pd.notna(row.get('n_recp_disp_sobu')) else 0.0,
                    'stot_inflows_inv_act': float(row['stot_inflows_inv_act']) if pd.notna(row.get('stot_inflows_inv_act')) else 0.0,
                    'c_pay_acq_const_fiolta': float(row['c_pay_acq_const_fiolta']) if pd.notna(row.get('c_pay_acq_const_fiolta')) else 0.0,
                    'c_paid_invest': float(row['c_paid_invest']) if pd.notna(row.get('c_paid_invest')) else 0.0,
                    'n_disp_subs_oth_biz': float(row['n_disp_subs_oth_biz']) if pd.notna(row.get('n_disp_subs_oth_biz')) else 0.0,
                    'oth_pay_ral_inv_act': float(row['oth_pay_ral_inv_act']) if pd.notna(row.get('oth_pay_ral_inv_act')) else 0.0,
                    'n_incr_pledge_loan': float(row['n_incr_pledge_loan']) if pd.notna(row.get('n_incr_pledge_loan')) else 0.0,
                    'stot_out_inv_act': float(row['stot_out_inv_act']) if pd.notna(row.get('stot_out_inv_act')) else 0.0,
                    'n_cashflow_inv_act': float(row['n_cashflow_inv_act']) if pd.notna(row.get('n_cashflow_inv_act')) else 0.0,
                    'c_recp_borrow': float(row['c_recp_borrow']) if pd.notna(row.get('c_recp_borrow')) else 0.0,
                    'proc_issue_bonds': float(row['proc_issue_bonds']) if pd.notna(row.get('proc_issue_bonds')) else 0.0,
                    'oth_cash_recp_ral_fnc_act': float(row['oth_cash_recp_ral_fnc_act']) if pd.notna(row.get('oth_cash_recp_ral_fnc_act')) else 0.0,
                    'stot_cash_in_fnc_act': float(row['stot_cash_in_fnc_act']) if pd.notna(row.get('stot_cash_in_fnc_act')) else 0.0,
                    'free_cashflow': float(row['free_cashflow']) if pd.notna(row.get('free_cashflow')) else 0.0,
                    'c_prepay_amt_borr': float(row['c_prepay_amt_borr']) if pd.notna(row.get('c_prepay_amt_borr')) else 0.0,
                    'c_pay_dist_dpcp_int_exp': float(row['c_pay_dist_dpcp_int_exp']) if pd.notna(row.get('c_pay_dist_dpcp_int_exp')) else 0.0,
                    'incl_dvd_profit_paid_sc_ms': float(row['incl_dvd_profit_paid_sc_ms']) if pd.notna(row.get('incl_dvd_profit_paid_sc_ms')) else 0.0,
                    'oth_cashpay_ral_fnc_act': float(row['oth_cashpay_ral_fnc_act']) if pd.notna(row.get('oth_cashpay_ral_fnc_act')) else 0.0,
                    'stot_cashout_fnc_act': float(row['stot_cashout_fnc_act']) if pd.notna(row.get('stot_cashout_fnc_act')) else 0.0,
                    'n_cash_flows_fnc_act': float(row['n_cash_flows_fnc_act']) if pd.notna(row.get('n_cash_flows_fnc_act')) else 0.0,
                    'eff_fx_flu_cash': float(row['eff_fx_flu_cash']) if pd.notna(row.get('eff_fx_flu_cash')) else 0.0,
                    'n_incr_cash_cash_equ': float(row['n_incr_cash_cash_equ']) if pd.notna(row.get('n_incr_cash_cash_equ')) else 0.0,
                    'c_cash_equ_beg_period': float(row['c_cash_equ_beg_period']) if pd.notna(row.get('c_cash_equ_beg_period')) else 0.0,
                    'c_cash_equ_end_period': float(row['c_cash_equ_end_period']) if pd.notna(row.get('c_cash_equ_end_period')) else 0.0,
                    'c_recp_cap_contrib': float(row['c_recp_cap_contrib']) if pd.notna(row.get('c_recp_cap_contrib')) else 0.0,
                    'incl_cash_rec_sg': float(row['incl_cash_rec_sg']) if pd.notna(row.get('incl_cash_rec_sg')) else 0.0,
                    'uncon_invest_loss': float(row['uncon_invest_loss']) if pd.notna(row.get('uncon_invest_loss')) else 0.0,
                    'prov_depr_assets': float(row['prov_depr_assets']) if pd.notna(row.get('prov_depr_assets')) else 0.0,
                    'depr_fa_coga_dpba': float(row['depr_fa_coga_dpba']) if pd.notna(row.get('depr_fa_coga_dpba')) else 0.0,
                    'amort_intang_assets': float(row['amort_intang_assets']) if pd.notna(row.get('amort_intang_assets')) else 0.0,
                    'lt_amort_deferred_exp': float(row['lt_amort_deferred_exp']) if pd.notna(row.get('lt_amort_deferred_exp')) else 0.0,
                    'decr_deferred_exp': float(row['decr_deferred_exp']) if pd.notna(row.get('decr_deferred_exp')) else 0.0,
                    'incr_acc_exp': float(row['incr_acc_exp']) if pd.notna(row.get('incr_acc_exp')) else 0.0,
                    'loss_disp_fiolta': float(row['loss_disp_fiolta']) if pd.notna(row.get('loss_disp_fiolta')) else 0.0,
                    'loss_scr_fa': float(row['loss_scr_fa']) if pd.notna(row.get('loss_scr_fa')) else 0.0,
                    'loss_fv_chg': float(row['loss_fv_chg']) if pd.notna(row.get('loss_fv_chg')) else 0.0,
                    'invest_loss': float(row['invest_loss']) if pd.notna(row.get('invest_loss')) else 0.0,
                    'decr_def_inc_tax_assets': float(row['decr_def_inc_tax_assets']) if pd.notna(row.get('decr_def_inc_tax_assets')) else 0.0,
                    'incr_def_inc_tax_liab': float(row['incr_def_inc_tax_liab']) if pd.notna(row.get('incr_def_inc_tax_liab')) else 0.0,
                    'decr_inventories': float(row['decr_inventories']) if pd.notna(row.get('decr_inventories')) else 0.0,
                    'decr_oper_payable': float(row['decr_oper_payable']) if pd.notna(row.get('decr_oper_payable')) else 0.0,
                    'incr_oper_payable': float(row['incr_oper_payable']) if pd.notna(row.get('incr_oper_payable')) else 0.0,
                    'others': float(row['others']) if pd.notna(row.get('others')) else 0.0,
                    'im_net_cashflow_oper_act': float(row['im_net_cashflow_oper_act']) if pd.notna(row.get('im_net_cashflow_oper_act')) else 0.0,
                    'conv_debt_into_cap': float(row['conv_debt_into_cap']) if pd.notna(row.get('conv_debt_into_cap')) else 0.0,
                    'conv_copbonds_due_within_1y': float(row['conv_copbonds_due_within_1y']) if pd.notna(row.get('conv_copbonds_due_within_1y')) else 0.0,
                    'fa_fnc_leases': float(row['fa_fnc_leases']) if pd.notna(row.get('fa_fnc_leases')) else 0.0,
                    'im_n_incr_cash_equ': float(row['im_n_incr_cash_equ']) if pd.notna(row.get('im_n_incr_cash_equ')) else 0.0,
                    'net_dism_capital_add': float(row['net_dism_capital_add']) if pd.notna(row.get('net_dism_capital_add')) else 0.0,
                    'net_cash_rece_sec': float(row['net_cash_rece_sec']) if pd.notna(row.get('net_cash_rece_sec')) else 0.0,
                    'credit_impa_loss': float(row['credit_impa_loss']) if pd.notna(row.get('credit_impa_loss')) else 0.0,
                    'use_sett_prov': float(row['use_sett_prov']) if pd.notna(row.get('use_sett_prov')) else 0.0,
                    'oth_loss_assets': float(row['oth_loss_assets']) if pd.notna(row.get('oth_loss_assets')) else 0.0,
                    'end_bal_cash': float(row['end_bal_cash']) if pd.notna(row.get('end_bal_cash')) else 0.0,
                    'beg_bal_cash': float(row['beg_bal_cash']) if pd.notna(row.get('beg_bal_cash')) else 0.0,
                    'end_bal_cash_equ': float(row['end_bal_cash_equ']) if pd.notna(row.get('end_bal_cash_equ')) else 0.0,
                    'beg_bal_cash_equ': float(row['beg_bal_cash_equ']) if pd.notna(row.get('beg_bal_cash_equ')) else 0.0,
                    'update_flag': float(row['update_flag']) if pd.notna(row.get('update_flag')) else 0.0
                })
            
            return cash_flow_data
            
        except Exception as e:
            print(f"Error fetching cash flow for {ts_code}: {e}")
            return []

    def get_income_statement(self, ts_code, start_date='', end_date='', fields=''):
        """
        Get income statement data from Tushare
        Reference: https://tushare.pro/document/2?doc_id=219
        """
        try:
            # Get income statement data
            df = self.pro.income(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields=fields if fields else 'ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps,total_revenue,revenue,int_income,prem_earned,comm_income,n_commis_income,n_oth_income,n_oth_biz_income,prem_income,out_prem,une_prem_reser,reins_income,n_sec_tb_income,n_undwrt_sec_income,n_indemnity_reser,n_ins_rsrv_rec,n_disp_tfa,n_disp_faas,n_disp_oth_assets,n_disp_oth_fa,n_disp_fiolta,n_disp_cip,n_disp_bio_assets,n_disp_mi,n_disp_oth_nca,n_disp_subs_oth_biz,n_oth_fa,n_disp_oth_biz,n_oth_comp_income,n_oth_comp_income_attr_p,n_oth_comp_income_attr_m_s,n_oth_comp_income_atsopc,n_oth_comp_income_attr_m_s_atsopc,n_oth_comp_income_atsop,n_income_attr_p,n_income_attr_m_s,n_income_discontinued,n_income_attr_p_discontinued,n_income_attr_m_s_discontinued,n_income_attr_p_ci,n_income_attr_m_s_ci,n_income,n_income_bef_na,n_income_bef_na_attr_p,n_income_bef_na_attr_m_s,n_income_bef_na_discontinued,n_income_bef_na_attr_p_discontinued,n_income_bef_na_attr_m_s_discontinued,n_income_bef_na_attr_p_ci,n_income_bef_na_attr_m_s_ci,n_income_bef_na_atsopc,n_income_bef_na_attr_p_atsopc,n_income_bef_na_attr_m_s_atsopc,n_income_bef_na_discontinued_atsopc,n_income_bef_na_attr_p_discontinued_atsopc,n_income_bef_na_attr_m_s_discontinued_atsopc,n_income_bef_na_attr_p_ci_atsopc,n_income_bef_na_attr_m_s_ci_atsopc,net_profit,net_profit_attr_p,net_profit_attr_m_s,net_profit_discontinued,net_profit_attr_p_discontinued,net_profit_attr_m_s_discontinued,net_profit_attr_p_ci,net_profit_attr_m_s_ci,net_profit_atsopc,net_profit_attr_p_atsopc,net_profit_attr_m_s_atsopc,net_profit_discontinued_atsopc,net_profit_attr_p_discontinued_atsopc,net_profit_attr_m_s_discontinued_atsopc,net_profit_attr_p_ci_atsopc,net_profit_attr_m_s_ci_atsopc,update_flag'
            )
            
            if df.empty:
                return []
            
            # Convert DataFrame to list of dictionaries
            income_statement_data = []
            for _, row in df.iterrows():
                income_statement_data.append({
                    'ts_code': row['ts_code'] if 'ts_code' in row else '',
                    'ann_date': str(row['ann_date']) if pd.notna(row.get('ann_date')) else '',
                    'f_ann_date': str(row['f_ann_date']) if pd.notna(row.get('f_ann_date')) else '',
                    'end_date': str(row['end_date']) if pd.notna(row.get('end_date')) else '',
                    'report_type': row['report_type'] if 'report_type' in row else '',
                    'comp_type': row['comp_type'] if 'comp_type' in row else '',
                    'basic_eps': float(row['basic_eps']) if pd.notna(row.get('basic_eps')) else 0.0,
                    'diluted_eps': float(row['diluted_eps']) if pd.notna(row.get('diluted_eps')) else 0.0,
                    'total_revenue': float(row['total_revenue']) if pd.notna(row.get('total_revenue')) else 0.0,
                    'revenue': float(row['revenue']) if pd.notna(row.get('revenue')) else 0.0,
                    'int_income': float(row['int_income']) if pd.notna(row.get('int_income')) else 0.0,
                    'prem_earned': float(row['prem_earned']) if pd.notna(row.get('prem_earned')) else 0.0,
                    'comm_income': float(row['comm_income']) if pd.notna(row.get('comm_income')) else 0.0,
                    'n_commis_income': float(row['n_commis_income']) if pd.notna(row.get('n_commis_income')) else 0.0,
                    'n_oth_income': float(row['n_oth_income']) if pd.notna(row.get('n_oth_income')) else 0.0,
                    'n_oth_biz_income': float(row['n_oth_biz_income']) if pd.notna(row.get('n_oth_biz_income')) else 0.0,
                    'prem_income': float(row['prem_income']) if pd.notna(row.get('prem_income')) else 0.0,
                    'out_prem': float(row['out_prem']) if pd.notna(row.get('out_prem')) else 0.0,
                    'une_prem_reser': float(row['une_prem_reser']) if pd.notna(row.get('une_prem_reser')) else 0.0,
                    'reins_income': float(row['reins_income']) if pd.notna(row.get('reins_income')) else 0.0,
                    'n_sec_tb_income': float(row['n_sec_tb_income']) if pd.notna(row.get('n_sec_tb_income')) else 0.0,
                    'n_undwrt_sec_income': float(row['n_undwrt_sec_income']) if pd.notna(row.get('n_undwrt_sec_income')) else 0.0,
                    'n_indemnity_reser': float(row['n_indemnity_reser']) if pd.notna(row.get('n_indemnity_reser')) else 0.0,
                    'n_ins_rsrv_rec': float(row['n_ins_rsrv_rec']) if pd.notna(row.get('n_ins_rsrv_rec')) else 0.0,
                    'n_disp_tfa': float(row['n_disp_tfa']) if pd.notna(row.get('n_disp_tfa')) else 0.0,
                    'n_disp_faas': float(row['n_disp_faas']) if pd.notna(row.get('n_disp_faas')) else 0.0,
                    'n_disp_oth_assets': float(row['n_disp_oth_assets']) if pd.notna(row.get('n_disp_oth_assets')) else 0.0,
                    'n_disp_oth_fa': float(row['n_disp_oth_fa']) if pd.notna(row.get('n_disp_oth_fa')) else 0.0,
                    'n_disp_fiolta': float(row['n_disp_fiolta']) if pd.notna(row.get('n_disp_fiolta')) else 0.0,
                    'n_disp_cip': float(row['n_disp_cip']) if pd.notna(row.get('n_disp_cip')) else 0.0,
                    'n_disp_bio_assets': float(row['n_disp_bio_assets']) if pd.notna(row.get('n_disp_bio_assets')) else 0.0,
                    'n_disp_mi': float(row['n_disp_mi']) if pd.notna(row.get('n_disp_mi')) else 0.0,
                    'n_disp_oth_nca': float(row['n_disp_oth_nca']) if pd.notna(row.get('n_disp_oth_nca')) else 0.0,
                    'n_disp_subs_oth_biz': float(row['n_disp_subs_oth_biz']) if pd.notna(row.get('n_disp_subs_oth_biz')) else 0.0,
                    'n_oth_fa': float(row['n_oth_fa']) if pd.notna(row.get('n_oth_fa')) else 0.0,
                    'n_disp_oth_biz': float(row['n_disp_oth_biz']) if pd.notna(row.get('n_disp_oth_biz')) else 0.0,
                    'n_oth_comp_income': float(row['n_oth_comp_income']) if pd.notna(row.get('n_oth_comp_income')) else 0.0,
                    'n_oth_comp_income_attr_p': float(row['n_oth_comp_income_attr_p']) if pd.notna(row.get('n_oth_comp_income_attr_p')) else 0.0,
                    'n_oth_comp_income_attr_m_s': float(row['n_oth_comp_income_attr_m_s']) if pd.notna(row.get('n_oth_comp_income_attr_m_s')) else 0.0,
                    'n_oth_comp_income_atsopc': float(row['n_oth_comp_income_atsopc']) if pd.notna(row.get('n_oth_comp_income_atsopc')) else 0.0,
                    'n_oth_comp_income_attr_m_s_atsopc': float(row['n_oth_comp_income_attr_m_s_atsopc']) if pd.notna(row.get('n_oth_comp_income_attr_m_s_atsopc')) else 0.0,
                    'n_oth_comp_income_atsop': float(row['n_oth_comp_income_atsop']) if pd.notna(row.get('n_oth_comp_income_atsop')) else 0.0,
                    'n_income_attr_p': float(row['n_income_attr_p']) if pd.notna(row.get('n_income_attr_p')) else 0.0,
                    'n_income_attr_m_s': float(row['n_income_attr_m_s']) if pd.notna(row.get('n_income_attr_m_s')) else 0.0,
                    'n_income_discontinued': float(row['n_income_discontinued']) if pd.notna(row.get('n_income_discontinued')) else 0.0,
                    'n_income_attr_p_discontinued': float(row['n_income_attr_p_discontinued']) if pd.notna(row.get('n_income_attr_p_discontinued')) else 0.0,
                    'n_income_attr_m_s_discontinued': float(row['n_income_attr_m_s_discontinued']) if pd.notna(row.get('n_income_attr_m_s_discontinued')) else 0.0,
                    'n_income_attr_p_ci': float(row['n_income_attr_p_ci']) if pd.notna(row.get('n_income_attr_p_ci')) else 0.0,
                    'n_income_attr_m_s_ci': float(row['n_income_attr_m_s_ci']) if pd.notna(row.get('n_income_attr_m_s_ci')) else 0.0,
                    'n_income': float(row['n_income']) if pd.notna(row.get('n_income')) else 0.0,
                    'n_income_bef_na': float(row['n_income_bef_na']) if pd.notna(row.get('n_income_bef_na')) else 0.0,
                    'n_income_bef_na_attr_p': float(row['n_income_bef_na_attr_p']) if pd.notna(row.get('n_income_bef_na_attr_p')) else 0.0,
                    'n_income_bef_na_attr_m_s': float(row['n_income_bef_na_attr_m_s']) if pd.notna(row.get('n_income_bef_na_attr_m_s')) else 0.0,
                    'n_income_bef_na_discontinued': float(row['n_income_bef_na_discontinued']) if pd.notna(row.get('n_income_bef_na_discontinued')) else 0.0,
                    'n_income_bef_na_attr_p_discontinued': float(row['n_income_bef_na_attr_p_discontinued']) if pd.notna(row.get('n_income_bef_na_attr_p_discontinued')) else 0.0,
                    'n_income_bef_na_attr_m_s_discontinued': float(row['n_income_bef_na_attr_m_s_discontinued']) if pd.notna(row.get('n_income_bef_na_attr_m_s_discontinued')) else 0.0,
                    'n_income_bef_na_attr_p_ci': float(row['n_income_bef_na_attr_p_ci']) if pd.notna(row.get('n_income_bef_na_attr_p_ci')) else 0.0,
                    'n_income_bef_na_attr_m_s_ci': float(row['n_income_bef_na_attr_m_s_ci']) if pd.notna(row.get('n_income_bef_na_attr_m_s_ci')) else 0.0,
                    'n_income_bef_na_atsopc': float(row['n_income_bef_na_atsopc']) if pd.notna(row.get('n_income_bef_na_atsopc')) else 0.0,
                    'n_income_bef_na_attr_p_atsopc': float(row['n_income_bef_na_attr_p_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_p_atsopc')) else 0.0,
                    'n_income_bef_na_attr_m_s_atsopc': float(row['n_income_bef_na_attr_m_s_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_m_s_atsopc')) else 0.0,
                    'n_income_bef_na_discontinued_atsopc': float(row['n_income_bef_na_discontinued_atsopc']) if pd.notna(row.get('n_income_bef_na_discontinued_atsopc')) else 0.0,
                    'n_income_bef_na_attr_p_discontinued_atsopc': float(row['n_income_bef_na_attr_p_discontinued_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_p_discontinued_atsopc')) else 0.0,
                    'n_income_bef_na_attr_m_s_discontinued_atsopc': float(row['n_income_bef_na_attr_m_s_discontinued_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_m_s_discontinued_atsopc')) else 0.0,
                    'n_income_bef_na_attr_p_ci_atsopc': float(row['n_income_bef_na_attr_p_ci_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_p_ci_atsopc')) else 0.0,
                    'n_income_bef_na_attr_m_s_ci_atsopc': float(row['n_income_bef_na_attr_m_s_ci_atsopc']) if pd.notna(row.get('n_income_bef_na_attr_m_s_ci_atsopc')) else 0.0,
                    'net_profit': float(row['net_profit']) if pd.notna(row.get('net_profit')) else 0.0,
                    'net_profit_attr_p': float(row['net_profit_attr_p']) if pd.notna(row.get('net_profit_attr_p')) else 0.0,
                    'net_profit_attr_m_s': float(row['net_profit_attr_m_s']) if pd.notna(row.get('net_profit_attr_m_s')) else 0.0,
                    'net_profit_discontinued': float(row['net_profit_discontinued']) if pd.notna(row.get('net_profit_discontinued')) else 0.0,
                    'net_profit_attr_p_discontinued': float(row['net_profit_attr_p_discontinued']) if pd.notna(row.get('net_profit_attr_p_discontinued')) else 0.0,
                    'net_profit_attr_m_s_discontinued': float(row['net_profit_attr_m_s_discontinued']) if pd.notna(row.get('net_profit_attr_m_s_discontinued')) else 0.0,
                    'net_profit_attr_p_ci': float(row['net_profit_attr_p_ci']) if pd.notna(row.get('net_profit_attr_p_ci')) else 0.0,
                    'net_profit_attr_m_s_ci': float(row['net_profit_attr_m_s_ci']) if pd.notna(row.get('net_profit_attr_m_s_ci')) else 0.0,
                    'net_profit_atsopc': float(row['net_profit_atsopc']) if pd.notna(row.get('net_profit_atsopc')) else 0.0,
                    'net_profit_attr_p_atsopc': float(row['net_profit_attr_p_atsopc']) if pd.notna(row.get('net_profit_attr_p_atsopc')) else 0.0,
                    'net_profit_attr_m_s_atsopc': float(row['net_profit_attr_m_s_atsopc']) if pd.notna(row.get('net_profit_attr_m_s_atsopc')) else 0.0,
                    'net_profit_discontinued_atsopc': float(row['net_profit_discontinued_atsopc']) if pd.notna(row.get('net_profit_discontinued_atsopc')) else 0.0,
                    'net_profit_attr_p_discontinued_atsopc': float(row['net_profit_attr_p_discontinued_atsopc']) if pd.notna(row.get('net_profit_attr_p_discontinued_atsopc')) else 0.0,
                    'net_profit_attr_m_s_discontinued_atsopc': float(row['net_profit_attr_m_s_discontinued_atsopc']) if pd.notna(row.get('net_profit_attr_m_s_discontinued_atsopc')) else 0.0,
                    'net_profit_attr_p_ci_atsopc': float(row['net_profit_attr_p_ci_atsopc']) if pd.notna(row.get('net_profit_attr_p_ci_atsopc')) else 0.0,
                    'net_profit_attr_m_s_ci_atsopc': float(row['net_profit_attr_m_s_ci_atsopc']) if pd.notna(row.get('net_profit_attr_m_s_ci_atsopc')) else 0.0,
                    'update_flag': float(row['update_flag']) if pd.notna(row.get('update_flag')) else 0.0
                })
            
            return income_statement_data
            
        except Exception as e:
            print(f"Error fetching income statement for {ts_code}: {e}")
            return []

if __name__ == "__main__":
    # Test the service
    service = TushareService()
    tickers = service.get_all_tickers()
    print(f"Found {len(tickers)} tickers")
    
    if tickers:
        sample_ticker = tickers[0]
        holders = service.get_top_holders(sample_ticker['ts_code'])
        print(f"Sample ticker: {sample_ticker['name']} - {len(holders)} holders found")
    
    # Test market players
    players = service.get_market_players()
    print(f"Found {len(players)} market players")
    
    # Test player transactions (if we have players)
    if players:
        sample_player = players[0]
        transactions = service.get_player_transactions(player_code=sample_player['code'])
        print(f"Sample player: {sample_player['name']} - {len(transactions)} transactions found")
