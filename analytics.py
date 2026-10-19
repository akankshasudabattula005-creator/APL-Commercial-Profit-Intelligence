"""Auditable line-level supply-chain profitability calculations."""
import numpy as np
import pandas as pd
NUMERIC=['Sales','Order Item Discount','Order Item Total','Order Profit Per Order','Benefit per order','Order Item Discount Rate','Order Item Quantity','Days for shipping (real)','Days for shipment (scheduled)']
DIMENSIONS=['Customer Segment','Market','Order Region','Order Country','Category Name','Product Name','Shipping Mode']

def prepare(data):
    d=data.copy()
    missing=[c for c in NUMERIC+DIMENSIONS+['Customer Id'] if c not in d.columns]
    if missing: raise ValueError('Missing required columns: '+', '.join(missing))
    for c in NUMERIC:d[c]=pd.to_numeric(d[c],errors='coerce')
    d['gross_sales']=d['Sales'];d['discount']=d['Order Item Discount'];d['net_sales']=d['Order Item Total'];d['profit']=d['Order Profit Per Order']
    d['reconciliation_error']=d.gross_sales-d.discount-d.net_sales
    d['valid_financial']=d[['gross_sales','discount','net_sales','profit']].notna().all(axis=1)&(d.gross_sales>0)&(d.net_sales>0)&(d.discount>=0)&(d.reconciliation_error.abs()<=0.05)
    d['loss_line']=d.profit<0
    d['late_flag']=pd.to_numeric(d.get('Late_delivery_risk',pd.Series(0,index=d.index)),errors='coerce').fillna(0)
    d['margin_pct']=np.where(d.net_sales>0,100*d.profit/d.net_sales,np.nan)
    return d

def metrics(d):
    gross=float(d.gross_sales.sum());disc=float(d.discount.sum());rev=float(d.net_sales.sum());profit=float(d.profit.sum())
    return {'lines':len(d),'gross':gross,'discount':disc,'revenue':rev,'profit':profit,'margin_pct':100*profit/rev if rev else np.nan,'loss_lines':int((d.profit<0).sum()),'loss_amount':float(-d.loc[d.profit<0,'profit'].sum()),'late_rate_pct':100*d.late_flag.mean() if len(d) else np.nan}

def aggregate(d,keys):
    keys=[keys] if isinstance(keys,str) else keys
    t=d.groupby(keys,dropna=False,observed=False).agg(revenue=('net_sales','sum'),gross=('gross_sales','sum'),discount=('discount','sum'),profit=('profit','sum'),lines=('profit','size'),loss_lines=('loss_line','sum'),late_rate=('late_flag','mean')).reset_index()
    t['margin_pct']=np.where(t.revenue>0,100*t.profit/t.revenue,np.nan)
    t['discount_pct']=np.where(t.gross>0,100*t.discount/t.gross,np.nan)
    t['late_rate']=t.late_rate*100
    return t

def customer_table(d):
    t=aggregate(d,'Customer Id')
    t['tier']='Core';t.loc[t.profit<0,'tier']='Loss-making'
    positive=t[t.profit>=0]
    if len(positive):
        q=positive.profit.quantile(.8)
        t.loc[(t.profit>=q)&(t.profit>=0),'tier']='Top profit contributors'
        t.loc[(t.profit>=0)&(t.margin_pct<metrics(d)['margin_pct']),'tier']='Below portfolio margin'
        t.loc[(t.profit>=q)&(t.profit>=0),'tier']='Top profit contributors'
    return t

def scenario(d,change_pp):
    # Discount shift is applied to the observed discount RATE, then bounded to [0,100%].
    old=d.discount.fillna(0).to_numpy(dtype=float)
    gross=d.gross_sales.to_numpy(dtype=float)
    new=np.clip(old+gross*change_pp/100,0,gross)
    new_rev=float((gross-new).sum())
    new_profit=float((d.profit.to_numpy(dtype=float)-(new-old)).sum())
    return {'revenue':new_rev,'profit':new_profit,'margin_pct':100*new_profit/new_rev if new_rev else np.nan,'delta_profit':new_profit-float(d.profit.sum()),'discount':float(new.sum())}

def discount_bands(d):
    x=d.copy();x['Discount band']=pd.cut(100*x['Order Item Discount Rate'],bins=[-0.01,0,5,10,15,20,30,50,100.1],labels=['0%','0–5%','5–10%','10–15%','15–20%','20–30%','30–50%','50–100%'],include_lowest=True)
    return aggregate(x,'Discount band')
