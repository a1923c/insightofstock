from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('.env')

""" 
1. tickers - Stock ticker information and basic company details
2. top_holders - Top shareholders data for each stock
3. hm_list - Market players/institutions list
4. hm_detail - Player transaction details and activities
5. balance_sheets - Financial balance sheets data
6. cash_flows - Cash flow statements
7. income_statements - Income and profit statements
8. fina_indicators - Key financial indicators and ratios
9. daily_basic - Daily basic market data and trading info
10. ths_hot - THS hot concept and theme data
11. dc_hot - DC hot concept and market attention data
12. daily - Daily market data
13. adj_factor - Adjust factors for stock prices
14. dividend - Dividend data
15. index_daily -  Index daily data
"""

Base = declarative_base()

class Ticker(Base):
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), nullable=False)  # TS代码
    symbol = Column(String(10))  # 股票代码
    name = Column(String(100))  # 股票名称
    area = Column(String(50))  # 地域
    industry = Column(String(50))  # 所属行业
    list_date = Column(String(10))  # 上市日期
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    top_holders = relationship("TopHolder", back_populates="ticker")
    daily_basic = relationship("DailyBasic", back_populates="ticker")
    ths_hots = relationship("ThsHot", back_populates="ticker")
    dc_hots = relationship("DcHot", back_populates="ticker")
    balance_sheets = relationship("BalanceSheet", back_populates="ticker")
    cash_flows = relationship("CashFlow", back_populates="ticker")
    income_statements = relationship("IncomeStatement", back_populates="ticker")
    fina_indicators = relationship("FinaIndicator", back_populates="ticker")
    daily_records = relationship("Daily", back_populates="ticker")
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
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)  # TS股票代码
    ann_date = Column(String(10))  # 公告日期
    f_ann_date = Column(String(10))  # 实际公告日期
    end_date = Column(String(10))  # 报告期
    report_type = Column(String(10))  # 报表类型
    comp_type = Column(String(10))  # 公司类型(1一般工商业2银行3保险4证券)
    end_type = Column(String(10))  # 报告期类型
    total_share = Column(Float)  # 期末总股本
    cap_rese = Column(Float)  # 资本公积金
    undistr_porfit = Column(Float)  # 未分配利润
    surplus_rese = Column(Float)  # 盈余公积金
    special_rese = Column(Float)  # 专项储备
    money_cap = Column(Float)  # 货币资金
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

class FinaIndicator(Base):
    __tablename__ = 'fina_indicators'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    ann_date = Column(String(10))
    end_date = Column(String(10))
    eps = Column(Float)  # 基本每股收益
    dt_eps = Column(Float)  # 稀释每股收益
    total_revenue_ps = Column(Float)  # 每股营业总收入
    revenue_ps = Column(Float)  # 每股营业收入
    capital_rese_ps = Column(Float)  # 每股资本公积
    surplus_rese_ps = Column(Float)  # 每股盈余公积
    undist_profit_ps = Column(Float)  # 每股未分配利润
    extra_item = Column(Float)  # 非经常性损益
    profit_dedt = Column(Float)  # 扣除非经常性损益后的净利润
    gross_margin = Column(Float)  # 毛利率
    current_ratio = Column(Float)  # 流动比率
    quick_ratio = Column(Float)  # 速动比率
    cash_ratio = Column(Float)  # 保守速动比率
    invturn_days = Column(Float)  # 存货周转天数
    arturn_days = Column(Float)  # 应收账款周转天数
    inv_turn = Column(Float)  # 存货周转率
    ar_turn = Column(Float)  # 应收账款周转率
    ca_turn = Column(Float)  # 流动资产周转率
    fa_turn = Column(Float)  # 固定资产周转率
    assets_turn = Column(Float)  # 总资产周转率
    op_income = Column(Float)  # 经营活动净收益
    valuechange_income = Column(Float)  # 价值变动净收益
    interst_income = Column(Float)  # 利息费用
    daa = Column(Float)  # 折旧与摊销
    ebit = Column(Float)  # 息税前利润
    ebitda = Column(Float)  # 息税折旧摊销前利润
    fcff = Column(Float)  # 企业自由现金流量
    fcfe = Column(Float)  # 股权自由现金流量
    current_exint = Column(Float)  # 无息流动负债
    noncurrent_exint = Column(Float)  # 无息非流动负债
    interestdebt = Column(Float)  # 带息债务
    netdebt = Column(Float)  # 净债务
    tangible_asset = Column(Float)  # 有形资产
    working_capital = Column(Float)  # 营运资金
    networking_capital = Column(Float)  # 营运流动资本
    invest_capital = Column(Float)  # 全部投入资本
    retained_earnings = Column(Float)  # 留存收益
    diluted2_eps = Column(Float)  # 期末摊薄每股收益
    bps = Column(Float)  # 每股净资产
    ocfps = Column(Float)  # 每股经营活动产生的现金流量净额
    retainedps = Column(Float)  # 每股留存收益
    cfps = Column(Float)  # 每股现金流量净额
    ebit_ps = Column(Float)  # 每股息税前利润
    fcff_ps = Column(Float)  # 每股企业自由现金流量
    fcfe_ps = Column(Float)  # 每股股东自由现金流量
    netprofit_margin = Column(Float)  # 销售净利率
    grossprofit_margin = Column(Float)  # 销售毛利率
    cogs_of_sales = Column(Float)  # 销售成本率
    expense_of_sales = Column(Float)  # 销售期间费用率
    profit_to_gr = Column(Float)  # 净利润/营业总收入
    saleexp_to_gr = Column(Float)  # 销售费用/营业总收入
    adminexp_of_gr = Column(Float)  # 管理费用/营业总收入
    finaexp_of_gr = Column(Float)  # 财务费用/营业总收入
    impai_ttm = Column(Float)  # 资产减值损失/营业总收入
    gc_of_gr = Column(Float)  # 营业总成本/营业总收入
    op_of_gr = Column(Float)  # 营业利润/营业总收入
    ebit_of_gr = Column(Float)  # 息税前利润/营业总收入
    roe = Column(Float)  # 净资产收益率
    roe_waa = Column(Float)  # 加权平均净资产收益率
    roe_dt = Column(Float)  # 净资产收益率(扣除非经常损益)
    roa = Column(Float)  # 总资产报酬率
    npta = Column(Float)  # 总资产净利率
    roic = Column(Float)  # 投入资本回报率
    roe_yearly = Column(Float)  # 年化净资产收益率
    roa2_yearly = Column(Float)  # 年化总资产报酬率
    roe_avg = Column(Float)  # 平均净资产收益率(增发条件)
    opincome_of_ebt = Column(Float)  # 经营活动净收益/利润总额
    investincome_of_ebt = Column(Float)  # 价值变动净收益/利润总额
    n_op_profit_of_ebt = Column(Float)  # 营业外收支净额/利润总额
    tax_to_ebt = Column(Float)  # 所得税/利润总额
    dtprofit_to_profit = Column(Float)  # 扣除非经常损益后的净利润/净利润
    salescash_to_or = Column(Float)  # 销售商品提供劳务收到的现金/营业收入
    ocf_to_or = Column(Float)  # 经营活动产生的现金流量净额/营业收入
    ocf_to_opincome = Column(Float)  # 经营活动产生的现金流量净额/经营活动净收益
    capitalized_to_da = Column(Float)  # 资本支出/折旧和摊销
    debt_to_assets = Column(Float)  # 资产负债率
    assets_to_eqt = Column(Float)  # 权益乘数
    dp_assets_to_eqt = Column(Float)  # 产权比率
    ca_to_assets = Column(Float)  # 流动资产/总资产
    nca_to_assets = Column(Float)  # 非流动资产/总资产
    tbassets_to_total_assets = Column(Float)  # 有形资产/总资产
    int_to_talcap = Column(Float)  # 带息债务/全部投入资本
    eqt_to_talcapital = Column(Float)  # 归属于母公司的股东权益/全部投入资本
    currentdebt_to_debt = Column(Float)  # 流动负债/负债合计
    longdeb_to_debt = Column(Float)  # 非流动负债/负债合计
    ocf_to_shortdebt = Column(Float)  # 经营活动产生的现金流量净额/流动负债
    debt_to_eqt = Column(Float)  # 产权比率
    eqt_to_debt = Column(Float)  # 归属于母公司的股东权益/负债合计
    eqt_to_interestdebt = Column(Float)  # 归属于母公司的股东权益/带息债务
    tangibleasset_to_debt = Column(Float)  # 有形资产/负债合计
    tangasset_to_intdebt = Column(Float)  # 有形资产/带息债务
    tangibleasset_to_netdebt = Column(Float)  # 有形资产/净债务
    ocf_to_debt = Column(Float)  # 经营活动产生的现金流量净额/负债合计
    ocf_to_interestdebt = Column(Float)  # 经营活动产生的现金流量净额/带息债务
    ocf_to_netdebt = Column(Float)  # 经营活动产生的现金流量净额/净债务
    ebit_to_interest = Column(Float)  # 已获利息倍数(EBIT/利息费用)
    long_debt_to_working_capital = Column(Float)  # 长期债务与营运资金比率
    ebitda_to_debt = Column(Float)  # 息税折旧摊销前利润/负债合计
    turn_days = Column(Float)  # 营业周期
    roa_yearly = Column(Float)  # 年化总资产净利率
    roa_dp = Column(Float)  # 投资回报率
    fixed_assets = Column(Float)  # 固定资产合计
    profit_prefin_exp = Column(Float)  # 扣除财务费用前营业利润
    non_op_profit = Column(Float)  # 非营业利润
    op_to_ebt = Column(Float)  # 营业利润/利润总额
    nop_to_ebt = Column(Float)  # 非营业利润/利润总额
    ocf_to_profit = Column(Float)  # 经营活动产生的现金流量净额/营业利润
    cash_to_liqdebt = Column(Float)  # 货币资金/流动负债
    cash_to_liqdebt_withinterest = Column(Float)  # 货币资金/带息流动负债
    op_to_liqdebt = Column(Float)  # 营业利润/流动负债
    op_to_debt = Column(Float)  # 营业利润/负债合计
    roic_yearly = Column(Float)  # 年化投入资本回报率
    total_fa_trun = Column(Float)  # 固定资产合计周转率
    profit_to_op = Column(Float)  # 利润总额/营业利润
    q_opincome = Column(Float)  # 经营活动净收益单季度
    q_investincome = Column(Float)  # 价值变动净收益单季度
    q_dtprofit = Column(Float)  # 扣除非经常损益后的净利润单季度
    q_eps = Column(Float)  # 基本每股收益单季度
    q_netprofit_margin = Column(Float)  # 销售净利率单季度
    q_gsprofit_margin = Column(Float)  # 销售毛利率单季度
    q_exp_to_sales = Column(Float)  # 销售期间费用率单季度
    q_profit_to_gr = Column(Float)  # 净利润/营业总收入单季度
    q_saleexp_to_gr = Column(Float)  # 销售费用/营业总收入单季度
    q_adminexp_to_gr = Column(Float)  # 管理费用/营业总收入单季度
    q_finaexp_to_gr = Column(Float)  # 财务费用/营业总收入单季度
    q_impair_to_gr_ttm = Column(Float)  # 资产减值损失/营业总收入单季度
    q_gc_to_gr = Column(Float)  # 营业总成本/营业总收入单季度
    q_op_to_gr = Column(Float)  # 营业利润/营业总收入单季度
    q_roe = Column(Float)  # 净资产收益率单季度
    q_dt_roe = Column(Float)  # 净资产单季度收益率(扣除非经常损益)
    q_npta = Column(Float)  # 总资产净利率单季度
    q_opincome_to_ebt = Column(Float)  # 经营活动净收益/利润总额单季度
    q_investincome_to_ebt = Column(Float)  # 价值变动净收益/利润总额单季度
    q_dtprofit_to_profit = Column(Float)  # 扣除非经常损益后的净利润/净利润单季度
    q_salescash_to_or = Column(Float)  # 销售商品提供劳务收到的现金/营业收入单季度
    q_ocf_to_sales = Column(Float)  # 经营活动产生的现金流量净额/营业收入单季度
    q_ocf_to_opincome = Column(Float)  # 经营活动产生的现金流量净额/经营活动净收益单季度
    basic_eps_yoy = Column(Float)  # 基本每股收益同比增长率(%)
    dt_eps_yoy = Column(Float)  # 稀释每股收益同比增长率(%)
    cfps_yoy = Column(Float)  # 每股经营活动产生的现金流量净额同比增长率(%)
    op_yoy = Column(Float)  # 营业利润同比增长率(%)
    ebt_yoy = Column(Float)  # 利润总额同比增长率(%)
    netprofit_yoy = Column(Float)  # 归属母公司股东的净利润同比增长率(%)
    dt_netprofit_yoy = Column(Float)  # 归属母公司股东的净利润-扣除非经常损益同比增长率(%)
    ocf_yoy = Column(Float)  # 经营活动产生的现金流量净额同比增长率(%)
    roe_yoy = Column(Float)  # 净资产收益率同比增长率(%)
    bps_yoy = Column(Float)  # 每股净资产相对年初增长率(%)
    assets_yoy = Column(Float)  # 资产总计相对年初增长率(%)
    eqt_yoy = Column(Float)  # 归属母公司的股东权益相对年初增长率(%)
    tr_yoy = Column(Float)  # 营业总收入同比增长率(%)
    or_yoy = Column(Float)  # 营业收入同比增长率(%)
    q_gr_yoy = Column(Float)  # 营业总收入同比增长率(%)
    q_gr_qoq = Column(Float)  # 营业总收入环比增长率(%)
    q_sales_yoy = Column(Float)  # 营业收入同比增长率(%)
    q_sales_qoq = Column(Float)  # 营业收入环比增长率(%)
    q_op_yoy = Column(Float)  # 营业利润同比增长率(%)
    q_op_qoq = Column(Float)  # 营业利润环比增长率(%)
    q_profit_yoy = Column(Float)  # 净利润同比增长率(%)
    q_profit_qoq = Column(Float)  # 净利润环比增长率(%)
    q_netprofit_yoy = Column(Float)  # 归属母公司股东的净利润同比增长率(%)
    q_netprofit_qoq = Column(Float)  # 归属母公司股东的净利润环比增长率(%)
    equity_yoy = Column(Float)  # 净资产同比增长率
    tr_total = Column(Float)  # 营业总收入累计
    profit_total = Column(Float)  # 利润总额累计
    netprofit_total = Column(Float)  # 归属母公司股东的净利润累计
    netprofit_attr_p_total = Column(Float)  # 归属母公司股东的净利润累计
    or_total = Column(Float)  # 营业收入累计
    q_sales_chg = Column(Float)  # 营业收入单季度环比增长率
    q_op_chg = Column(Float)  # 营业利润单季度环比增长率
    q_netprofit_chg = Column(Float)  # 归属母公司股东的净利润单季度环比增长率
    q_netprofit_attr_p_chg = Column(Float)  # 归属母公司股东的净利润单季度环比增长率
    q_profit_chg = Column(Float)  # 净利润单季度环比增长率
    q_gr_chg = Column(Float)  # 营业总收入单季度环比增长率
    update_flag = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="fina_indicators")

class DailyBasic(Base):
    __tablename__ = 'daily_basic'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    trade_date = Column(String(10), nullable=False)
    turnover_rate = Column(Float)
    volume_ratio = Column(Float)
    pe = Column(Float)
    pe_ttm = Column(Float)
    pb = Column(Float)
    total_mv = Column(Float)
    float_mv = Column(Float)
    total_share = Column(Float)
    float_share = Column(Float)
    free_share = Column(Float)
    turnover_rate_f = Column(Float)
    close = Column(Float)
    circ_mv = Column(Float)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="daily_basic")

class ThsHot(Base):
    __tablename__ = 'ths_hot'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, nullable=False)        # 交易日期
    data_type = Column(String, nullable=False)         # 数据类型
    ts_code = Column(String, index=True, nullable=True)  # 股票代码 此处可以为空，因为热点不仅仅是股票
    ts_name = Column(String)                           # 股票名称
    rank = Column(Integer)                             # 排行
    pct_change = Column(Float)                         # 涨跌幅%
    current_price = Column(Float)                      # 当前价格
    concept = Column(String)                           # 标签
    rank_reason = Column(String)                       # 上榜解读
    hot = Column(Float)                                # 热度值
    rank_time = Column(String)                         # 排行榜获取时间
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: relationship to Ticker
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=True)
    ticker = relationship("Ticker", back_populates="ths_hots")

class DcHot(Base):
    __tablename__ = 'dc_hot'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_date = Column(String, nullable=False)        # 交易日期
    data_type = Column(String, nullable=False)         # 数据类型
    ts_code = Column(String, index=True, nullable=True)  # 股票代码 此处可以为空，因为热点不仅仅是股票
    ts_name = Column(String)                           # 股票名称
    rank = Column(Integer)                             # 排行或者热度
    pct_change = Column(Float)                         # 涨跌幅%
    current_price = Column(Float) 
    concept = Column(String)                           # 标签
    hot = Column(Float)                                # 热度值当前价
    rank_time = Column(String)                         # 排行榜获取时间
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: relationship to Ticker
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=True)
    ticker = relationship("Ticker", back_populates="dc_hots")

class LastDayQuarter(Base):
    __tablename__ = 'lastday_quarter'
    
    id = Column(Integer, primary_key=True)
    end_date = Column(String(10), nullable=False)

class Daily(Base):
    __tablename__ = 'daily'
    
    id = Column(Integer, primary_key=True)
    ts_code = Column(String(20), ForeignKey('tickers.ts_code'), nullable=False)
    trade_date = Column(String(10), nullable=False)
    open = Column(Float)  # 开盘价
    high = Column(Float)  # 最高价
    low = Column(Float)  # 最低价
    close = Column(Float)  # 收盘价
    pre_close = Column(Float)  # 昨收价
    change = Column(Float)  # 涨跌额
    pct_chg = Column(Float)  # 涨跌幅
    vol = Column(Float)  # 成交量（手）
    amount = Column(Float)  # 成交额（千元）
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    ticker = relationship("Ticker", back_populates="daily_records")

class AdjFactor(Base):
    __tablename__ = 'adj_factor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), index=True, nullable=False)
    trade_date = Column(String(8), index=True, nullable=False)
    adj_factor = Column(Float, nullable=False)
    updated_date = Column(DateTime, default=datetime.utcnow)

class Dividend(Base):
    __tablename__ = 'dividend'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), index=True, nullable=False)         # TS代码
    end_date = Column(String(10), nullable=False)                    # 分送年度
    ann_date = Column(String(10))                                    # 预案公告日（董事会）
    div_proc = Column(String(20))                                    # 实施进度
    stk_div = Column(Float)                                          # 每股送转
    stk_bo_rate = Column(Float)                                      # 每股送股比例
    stk_co_rate = Column(Float)                                      # 每股转增比例
    cash_div = Column(Float)                                         # 每股分红（税后）
    cash_div_tax = Column(Float)                                     # 每股分红（税前）
    record_date = Column(String(10))                                 # 股权登记日
    ex_date = Column(String(10))                                     # 除权除息日
    pay_date = Column(String(10))                                    # 派息日
    div_listdate = Column(String(10))                                # 红股上市日
    imp_ann_date = Column(String(10))                                # 实施公告日
    base_date = Column(String(10))                                   # 基准日
    base_share = Column(Float)                                       # 实施基准股本（万）
    update_flag = Column(String(5))                                  # 是否变更过（1表示变更）
    updated_date = Column(DateTime, default=datetime.utcnow)   
    
class IndexDaily(Base):
    __tablename__ = 'index_daily'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), index=True, nullable=False)         # 指数代码
    trade_date = Column(String(8), index=True, nullable=False)       # 交易日期
    close = Column(Float)                                            # 收盘点位
    open = Column(Float)                                             # 开盘点位
    high = Column(Float)                                             # 最高点位
    low = Column(Float)                                              # 最低点位
    pre_close = Column(Float)                                        # 昨日收盘点位
    change = Column(Float)                                           # 涨跌点
    pct_chg = Column(Float)                                          # 涨跌幅
    vol = Column(Float)                                              # 成交量（手）
    amount = Column(Float)                                           # 成交额（千元）
    updated_date = Column(DateTime, default=datetime.utcnow)         # 更新时间
      # 更新时间
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
        conn.execute(text("""
            CREATE VIEW IF NOT EXISTS recent_hot_stocks AS
            SELECT 
                trade_date, 
                ts_code, 
                ts_name, 
                'THS' AS Security_name 
            FROM ths_hot 
            WHERE data_type='热股' AND date(substr(trade_date,1,4)||'-'||substr(trade_date,5,2)||'-'||substr(trade_date,7,2))>=date('now','-7 days')
            UNION
            SELECT 
                trade_date, 
                ts_code,
                ts_name, 
                'DC' AS Security_name 
            FROM dc_hot 
            WHERE data_type='A股市场' AND date(substr(trade_date,1,4)||'-'||substr(trade_date,5,2)||'-'||substr(trade_date,7,2))>=date('now','-7 days');
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
