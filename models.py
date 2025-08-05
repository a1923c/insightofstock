from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/var/www/insightofstock/.env')

Base = declarative_base()

class Ticker(Base):
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), unique=True, nullable=False)
    symbol = Column(String(10))
    name = Column(String(100))
    area = Column(String(50))
    industry = Column(String(50))
    list_date = Column(String(10))
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    top_holders = relationship("TopHolder", back_populates="ticker")
    
    def __repr__(self):
        return f"<Ticker(ts_code='{self.ts_code}', name='{self.name}')>"

class TopHolder(Base):
    __tablename__ = 'top_holders'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    end_date = Column(String(10))
    holder_name = Column(String(100))
    hold_amount = Column(Float)
    hold_ratio = Column(Float)
    holder_type = Column(String(10))  # G=个人, C=机构, P=私募, E=信托, O=其他
    hold_change = Column(Float)  # 持股变动数量
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="top_holders")
    
    def __repr__(self):
        return f"<TopHolder(ts_code='{self.ts_code}', holder_name='{self.holder_name}', hold_ratio={self.hold_ratio})>"

class UpdateLog(Base):
    __tablename__ = 'update_log'
    
    id = Column(Integer, primary_key=True)
    update_type = Column(String(50), nullable=False)  # 'tickers', 'holders', 'full'
    last_update_date = Column(String(10), nullable=False)  # Latest end_date from data
    record_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UpdateLog(update_type='{self.update_type}', last_update_date='{self.last_update_date}')>"

class HmList(Base):
    __tablename__ = 'hm_list'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    desc = Column(String(200), nullable=True)
    orgs = Column(String(200), nullable=False)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    #transactions = relationship("PlayerTransaction", back_populates="player")

class HmDetail(Base):
    __tablename__ = 'hm_detail'
    
    id = Column(Integer, primary_key=True)
    trade_date = Column(String(10), nullable=False)
    ts_code = Column(String(20), nullable=False)
    ts_name = Column(String(20), nullable=False)
    buy_amount = Column(Float)
    sell_amount = Column(Float)
    name = Column(String(100), nullable=False)
    orgs = Column(String(200), nullable=False)
    net_amount = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BalanceSheet(Base):
    __tablename__ = 'balance_sheets'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    f_ann_date = Column(String(10))
    end_date = Column(String(10))
    report_type = Column(String(10))
    comp_type = Column(String(10))
    total_share = Column(Float)
    cap_rese = Column(Float)
    undist_profit = Column(Float)
    surplus_rese = Column(Float)
    special_rese = Column(Float)
    money_cap = Column(Float)
    trad_asset = Column(Float)
    notes_receiv = Column(Float)
    accounts_receiv = Column(Float)
    oth_receiv = Column(Float)
    prepayment = Column(Float)
    div_receiv = Column(Float)
    int_receiv = Column(Float)
    inventories = Column(Float)
    amor_exp = Column(Float)
    nca_within_1y = Column(Float)
    sett_rsrv = Column(Float)
    loanto_oth_bank_fi = Column(Float)
    premium_receiv = Column(Float)
    reinsur_receiv = Column(Float)
    reinsur_res_receiv = Column(Float)
    pur_resale_fa = Column(Float)
    oth_cur_assets = Column(Float)
    total_cur_assets = Column(Float)
    fa_avail_for_sale = Column(Float)
    htm_invest = Column(Float)
    lt_eqt_invest = Column(Float)
    invest_real_estate = Column(Float)
    time_deposits = Column(Float)
    oth_assets = Column(Float)
    lt_rec = Column(Float)
    fix_assets = Column(Float)
    cip = Column(Float)
    const_materials = Column(Float)
    fixed_assets_disp = Column(Float)
    produc_bio_assets = Column(Float)
    oil_and_gas_assets = Column(Float)
    intan_assets = Column(Float)
    r_and_d = Column(Float)
    goodwill = Column(Float)
    lt_amor_exp = Column(Float)
    defer_tax_assets = Column(Float)
    decr_in_disbur = Column(Float)
    oth_nca = Column(Float)
    total_nca = Column(Float)
    cash_reser_cb = Column(Float)
    depos_in_oth_bfi = Column(Float)
    prec_metals = Column(Float)
    deriv_assets = Column(Float)
    rr_reins_une_prem = Column(Float)
    rr_reins_outstd_cla = Column(Float)
    rr_reins_lins_liab = Column(Float)
    rr_reins_lthins_liab = Column(Float)
    refund_depos = Column(Float)
    ph_pledge_loans = Column(Float)
    refund_cap_depos = Column(Float)
    indep_acct_assets = Column(Float)
    client_depos = Column(Float)
    client_prov = Column(Float)
    transac_seat_fee = Column(Float)
    invest_as_receiv = Column(Float)
    total_assets = Column(Float)
    lt_borr = Column(Float)
    st_borr = Column(Float)
    cb_borr = Column(Float)
    depos_ib_deposits = Column(Float)
    loan_oth_bank = Column(Float)
    trading_fl = Column(Float)
    notes_payable = Column(Float)
    acct_payable = Column(Float)
    adv_receipts = Column(Float)
    sold_for_repur_fa = Column(Float)
    comm_payable = Column(Float)
    payroll_payable = Column(Float)
    taxes_payable = Column(Float)
    int_payable = Column(Float)
    div_payable = Column(Float)
    oth_payable = Column(Float)
    acc_exp = Column(Float)
    deferred_inc = Column(Float)
    st_bonds_payable = Column(Float)
    payable_to_reinsurer = Column(Float)
    rsrv_insur_cont = Column(Float)
    acting_trading_sec = Column(Float)
    acting_uw_sec = Column(Float)
    oth_cur_liab = Column(Float)
    total_cur_liab = Column(Float)
    bonds_payable = Column(Float)
    lt_payable = Column(Float)
    specific_payables = Column(Float)
    estim_liab = Column(Float)
    defer_tax_liab = Column(Float)
    defer_inc_non_cur = Column(Float)
    oth_ncl = Column(Float)
    total_ncl = Column(Float)
    deps_proc_sell_assets = Column(Float)
    reindebt_payable = Column(Float)
    policy_div_payable = Column(Float)
    total_liab = Column(Float)
    treasury_share = Column(Float)
    ordin_risk_reser = Column(Float)
    forex_differ = Column(Float)
    invest_loss_unconf = Column(Float)
    minority_int = Column(Float)
    total_hldr_eqy_exc_min_int = Column(Float)
    total_hldr_eqy_inc_min_int = Column(Float)
    total_liab_hldr_eqy = Column(Float)
    lt_payroll_payable = Column(Float)
    oth_comp_income = Column(Float)
    oth_eqt_tools = Column(Float)
    oth_eqt_tools_p_shr = Column(Float)
    lending_funds = Column(Float)
    acc_receivable = Column(Float)
    st_finl_co_borr = Column(Float)
    deposit = Column(Float)
    oth_assets_flag = Column(Float)
    update_flag = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="balance_sheets")

class CashFlow(Base):
    __tablename__ = 'cash_flows'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    f_ann_date = Column(String(10))
    end_date = Column(String(10))
    report_type = Column(String(10))
    comp_type = Column(String(10))
    net_profit = Column(Float)
    finan_exp = Column(Float)
    c_fr_sale_sg = Column(Float)
    recp_tax_rends = Column(Float)
    n_depos_incr_fi = Column(Float)
    n_incr_loans_cb = Column(Float)
    n_inc_borr_oth_fi = Column(Float)
    prem_fr_orig_contr = Column(Float)
    n_incr_insured_dep = Column(Float)
    n_reinsur_prem = Column(Float)
    n_incr_disp_tfa = Column(Float)
    ifc_cash_incr = Column(Float)
    n_incr_disp_faas = Column(Float)
    n_incr_loans_oth_bank = Column(Float)
    n_cap_incr_repur = Column(Float)
    c_fr_oth_operate_a = Column(Float)
    c_inf_fr_operate_a = Column(Float)
    c_paid_goods_s = Column(Float)
    c_paid_to_for_empl = Column(Float)
    c_paid_for_taxes = Column(Float)
    n_incr_clt_loan_cb = Column(Float)
    n_incr_dep_cbob = Column(Float)
    c_pay_claims_orig_inco = Column(Float)
    pay_handling_chrg = Column(Float)
    pay_comm_insur_plcy = Column(Float)
    oth_cash_pay_oper_act = Column(Float)
    st_cash_out_act = Column(Float)
    n_cashflow_act = Column(Float)
    oth_recp_ral_inv_act = Column(Float)
    c_disp_withdrwl_invest = Column(Float)
    c_recp_return_invest = Column(Float)
    n_recp_disp_fiolta = Column(Float)
    n_recp_disp_sobu = Column(Float)
    stot_inflows_inv_act = Column(Float)
    c_pay_acq_const_fiolta = Column(Float)
    c_paid_invest = Column(Float)
    n_disp_subs_oth_biz = Column(Float)
    oth_pay_ral_inv_act = Column(Float)
    n_incr_pledge_loan = Column(Float)
    stot_out_inv_act = Column(Float)
    n_cashflow_inv_act = Column(Float)
    c_recp_borrow = Column(Float)
    proc_issue_bonds = Column(Float)
    oth_cash_recp_ral_fnc_act = Column(Float)
    stot_cash_in_fnc_act = Column(Float)
    free_cashflow = Column(Float)
    c_prepay_amt_borr = Column(Float)
    c_pay_dist_dpcp_int_exp = Column(Float)
    incl_dvd_profit_paid_sc_ms = Column(Float)
    oth_cashpay_ral_fnc_act = Column(Float)
    stot_cashout_fnc_act = Column(Float)
    n_cash_flows_fnc_act = Column(Float)
    eff_fx_flu_cash = Column(Float)
    n_incr_cash_cash_equ = Column(Float)
    c_cash_equ_beg_period = Column(Float)
    c_cash_equ_end_period = Column(Float)
    c_recp_cap_contrib = Column(Float)
    incl_cash_rec_sg = Column(Float)
    uncon_invest_loss = Column(Float)
    prov_depr_assets = Column(Float)
    depr_fa_coga_dpba = Column(Float)
    amort_intang_assets = Column(Float)
    lt_amort_deferred_exp = Column(Float)
    decr_deferred_exp = Column(Float)
    incr_acc_exp = Column(Float)
    loss_disp_fiolta = Column(Float)
    loss_scr_fa = Column(Float)
    loss_fv_chg = Column(Float)
    invest_loss = Column(Float)
    decr_def_inc_tax_assets = Column(Float)
    incr_def_inc_tax_liab = Column(Float)
    decr_inventories = Column(Float)
    decr_oper_payable = Column(Float)
    incr_oper_payable = Column(Float)
    others = Column(Float)
    im_net_cashflow_oper_act = Column(Float)
    conv_debt_into_cap = Column(Float)
    conv_copbonds_due_within_1y = Column(Float)
    fa_fnc_leases = Column(Float)
    im_n_incr_cash_equ = Column(Float)
    net_dism_capital_add = Column(Float)
    net_cash_rece_sec = Column(Float)
    credit_impa_loss = Column(Float)
    use_sett_prov = Column(Float)
    oth_loss_assets = Column(Float)
    end_bal_cash = Column(Float)
    beg_bal_cash = Column(Float)
    end_bal_cash_equ = Column(Float)
    beg_bal_cash_equ = Column(Float)
    update_flag = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="cash_flows")

class IncomeStatement(Base):
    __tablename__ = 'income_statements'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    f_ann_date = Column(String(10))
    end_date = Column(String(10))
    report_type = Column(String(10))
    comp_type = Column(String(10))
    basic_eps = Column(Float)
    diluted_eps = Column(Float)
    total_revenue = Column(Float)
    revenue = Column(Float)
    int_income = Column(Float)
    prem_earned = Column(Float)
    comm_income = Column(Float)
    n_commis_income = Column(Float)
    n_oth_income = Column(Float)
    n_oth_biz_income = Column(Float)
    prem_income = Column(Float)
    out_prem = Column(Float)
    une_prem_reser = Column(Float)
    reins_income = Column(Float)
    n_sec_tb_income = Column(Float)
    n_undwrt_sec_income = Column(Float)
    n_indemnity_reser = Column(Float)
    n_ins_rsrv_rec = Column(Float)
    n_disp_tfa = Column(Float)
    n_disp_faas = Column(Float)
    n_disp_oth_assets = Column(Float)
    n_disp_oth_fa = Column(Float)
    n_disp_fiolta = Column(Float)
    n_disp_cip = Column(Float)
    n_disp_bio_assets = Column(Float)
    n_disp_mi = Column(Float)
    n_disp_oth_nca = Column(Float)
    n_disp_subs_oth_biz = Column(Float)
    n_oth_fa = Column(Float)
    n_disp_oth_biz = Column(Float)
    n_oth_comp_income = Column(Float)
    n_oth_comp_income_attr_p = Column(Float)
    n_oth_comp_income_attr_m_s = Column(Float)
    n_oth_comp_income_atsopc = Column(Float)
    n_oth_comp_income_attr_m_s_atsopc = Column(Float)
    n_oth_comp_income_atsop = Column(Float)
    n_income_attr_p = Column(Float)
    n_income_attr_m_s = Column(Float)
    n_income_discontinued = Column(Float)
    n_income_attr_p_discontinued = Column(Float)
    n_income_attr_m_s_discontinued = Column(Float)
    n_income_attr_p_ci = Column(Float)
    n_income_attr_m_s_ci = Column(Float)
    n_income = Column(Float)
    n_income_bef_na = Column(Float)
    n_income_bef_na_attr_p = Column(Float)
    n_income_bef_na_attr_m_s = Column(Float)
    n_income_bef_na_discontinued = Column(Float)
    n_income_bef_na_attr_p_discontinued = Column(Float)
    n_income_bef_na_attr_m_s_discontinued = Column(Float)
    n_income_bef_na_attr_p_ci = Column(Float)
    n_income_bef_na_attr_m_s_ci = Column(Float)
    n_income_bef_na_atsopc = Column(Float)
    n_income_bef_na_attr_p_atsopc = Column(Float)
    n_income_bef_na_attr_m_s_atsopc = Column(Float)
    n_income_bef_na_discontinued_atsopc = Column(Float)
    n_income_bef_na_attr_p_discontinued_atsopc = Column(Float)
    n_income_bef_na_attr_m_s_discontinued_atsopc = Column(Float)
    n_income_bef_na_attr_p_ci_atsopc = Column(Float)
    n_income_bef_na_attr_m_s_ci_atsopc = Column(Float)
    net_profit = Column(Float)
    net_profit_attr_p = Column(Float)
    net_profit_attr_m_s = Column(Float)
    net_profit_discontinued = Column(Float)
    net_profit_attr_p_discontinued = Column(Float)
    net_profit_attr_m_s_discontinued = Column(Float)
    net_profit_attr_p_ci = Column(Float)
    net_profit_attr_m_s_ci = Column(Float)
    net_profit_atsopc = Column(Float)
    net_profit_attr_p_atsopc = Column(Float)
    net_profit_attr_m_s_atsopc = Column(Float)
    net_profit_discontinued_atsopc = Column(Float)
    net_profit_attr_p_discontinued_atsopc = Column(Float)
    net_profit_attr_m_s_discontinued_atsopc = Column(Float)
    net_profit_attr_p_ci_atsopc = Column(Float)
    net_profit_attr_m_s_ci_atsopc = Column(Float)
    update_flag = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="income_statements")

# Add relationships to Ticker class
Ticker.balance_sheets = relationship("BalanceSheet", back_populates="ticker")
Ticker.cash_flows = relationship("CashFlow", back_populates="ticker")
Ticker.income_statements = relationship("IncomeStatement", back_populates="ticker")

# Database setup
def get_engine():
    database_url = os.getenv('DATABASE_URL', 'sqlite:///database/insightofstock.db')
    engine = create_engine(database_url)
    return engine

def create_tables():
    engine = get_engine()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create individual holder tickers view
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS individual_holder_tickers AS
            SELECT 
                holder_name,
                COUNT(DISTINCT ts_code) as ticker_count
            FROM top_holders 
            WHERE holder_type = '自然人' 
            GROUP BY holder_name
            HAVING ticker_count>=2 
            ORDER BY ticker_count DESC
        """))
        
        # Create tickers with multiple holders view (individual shareholders only)
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS tickers_with_multiple_holders AS
            SELECT 
                ts_code, 
                COUNT(DISTINCT holder_name) as holder_count 
            FROM top_holders 
            WHERE holder_type = '自然人' 
            GROUP BY ts_code
            HAVING holder_count>=2 
            ORDER BY holder_count DESC
        """))
        conn.commit()
    
    return engine

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
