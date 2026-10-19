from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from html import escape
from ui_helpers import compact_number, customer_rankings, chart_category_labels
from analytics import prepare,metrics,aggregate,customer_table,scenario,discount_bands
st.set_page_config(page_title='APL | Commercial Intelligence',page_icon='📈',layout='wide',initial_sidebar_state='expanded')
st.markdown("""<style>.block-container{padding-top:1.3rem;max-width:1550px}h1,h2,h3{letter-spacing:-.025em}.stMetric{padding:1.1rem;border:1px solid #334155;border-radius:14px;background:rgba(100,116,139,.08)}[data-testid=stSidebar]{border-right:1px solid #334155}div[data-testid=stTabs] button{font-weight:600}</style>""",unsafe_allow_html=True)
BASE=Path(__file__).resolve().parent
@st.cache_data(show_spinner='Loading and reconciling financial records...')
def read_file(path):return prepare(pd.read_csv(path,encoding='latin1',low_memory=False))
@st.cache_data(show_spinner='Validating uploaded data...')
def read_upload(contents):
    from io import BytesIO
    return prepare(pd.read_csv(BytesIO(contents),encoding='latin1',low_memory=False))
path=BASE/'data'/'APL_Logistics.csv'
st.title('Commercial Profit Intelligence')
st.caption('APL Logistics dataset case study  /  Customer · Product · Margin · Discount · Geography')
with st.sidebar:
    st.markdown('### CONTROL CENTER')
    source=st.radio('Data source',['Bundled dataset','Upload CSV'],horizontal=False)
    if source=='Upload CSV':
        uploaded=st.file_uploader('Transaction CSV',type='csv')
        if uploaded is None:st.info('Upload a CSV to proceed.');st.stop()
        raw=read_upload(uploaded.getvalue())
    else:raw=read_file(str(path))
    st.caption(f'{len(raw):,} source transaction lines')
    invalid=raw.loc[~raw.valid_financial]
    if len(invalid):st.warning(f'{len(invalid):,} invalid financial rows excluded from financial KPIs. See Audit.')
    raw_valid=raw.loc[raw.valid_financial].copy()
    selected={}
    for c in ['Market','Order Region','Customer Segment','Category Name','Product Name','Shipping Mode']:
        opts=sorted(raw_valid[c].dropna().astype(str).unique().tolist())
        selected[c]=st.multiselect(c,opts,placeholder='All '+c.lower())
    st.caption('All analyses use the same selected population. Empty filter = all.')
d=raw_valid
for c,v in selected.items():
    if v:d=d[d[c].isin(v)]
if d.empty:st.warning('No transactions match the filters. Clear one or more selections.');st.stop()
m=metrics(d)
def money(v):
    """Compact, readable monetary values for KPI cards and scenario deltas."""
    v = float(v)
    sign = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1_000_000_000:
        return f"{sign}{a / 1_000_000_000:,.2f}B CU"
    if a >= 1_000_000:
        return f"{sign}{a / 1_000_000:,.2f}M CU"
    if a >= 1_000:
        return f"{sign}{a / 1_000:,.1f}K CU"
    return f"{sign}{a:,.0f} CU"

def show_table(df, percent_columns=("margin_pct", "discount_pct", "late_rate")):
    """Format financial tables without changing underlying export precision."""
    formats = {
        c: "{:,.2f}" for c in ("revenue", "gross", "discount", "profit")
        if c in df.columns
    }
    formats.update({c: "{:.2f}%" for c in percent_columns if c in df.columns})
    styled = df.style.format(formats, na_rep="—")
    if "profit" in df.columns:
        styled = styled.map(
            lambda v: "color: #fb7185; font-weight: 700" if pd.notna(v) and v < 0 else "",
            subset=["profit"],
        )
    if "margin_pct" in df.columns:
        styled = styled.map(
            lambda v: "color: #fb7185; font-weight: 700" if pd.notna(v) and v < 0 else "",
            subset=["margin_pct"],
        )
    st.dataframe(styled, hide_index=True, width="stretch")
def dl(t,name):st.download_button('Export '+name,t.to_csv(index=False).encode(),file_name=name+'.csv',mime='text/csv',key=name)
def bars(t, x, y, title, n=15, ranking='top'):
    """Plot top/bottom ranks on a categorical axis, never a numeric ID axis."""
    if t.empty:
        st.info('No data available for this chart.')
        return
    t = t.copy()
    if x == 'Customer Id' and y == 'profit':
        top, bottom = customer_rankings(t, n)
        t = (bottom if ranking == 'bottom' else top).sort_values(y, ascending=(ranking != 'bottom'))
    elif ranking == 'bottom':
        t = t.nsmallest(n, y).sort_values(y, ascending=False)
    else:
        t = t.nlargest(n, y).sort_values(y, ascending=True)
    t['_category_label'] = chart_category_labels(t[x])
    fig = px.bar(
        t, x=y, y='_category_label', orientation='h',
        title=title, text=y,
        color_discrete_sequence=['#14b8a6' if ranking != 'bottom' else '#fb7185'],
    )
    fig.update_traces(texttemplate='%{x:,.0f}', textposition='outside', cliponaxis=False,
                      hovertemplate='%{y}<br>' + y + ': %{x:,.2f}<extra></extra>')
    fig.update_yaxes(type='category', title_text=x, categoryorder='array',
                     categoryarray=t['_category_label'].tolist())
    fig.update_xaxes(title_text=y.replace('_', ' ').title(), zeroline=True)
    fig.update_layout(height=max(380, min(680, 31 * len(t) + 130)),
                      margin=dict(l=12, r=75, t=60, b=20),
                      showlegend=False)
    st.plotly_chart(fig, width='stretch')

# HTML KPI cards prevent Streamlit metric's narrow-column ellipsis.
kpi_items = [
    ('Net revenue', compact_number(m['revenue'])),
    ('Recorded profit', compact_number(m['profit'])),
    ('Weighted margin', f"{m['margin_pct']:.2f}%"),
    ('Gross sales', compact_number(m['gross'])),
    ('Discounts', compact_number(m['discount'])),
    ('Loss-making lines', f"{m['loss_lines']:,}"),
]
kpi_html = ''.join(
    '<div class="apl-kpi"><div class="apl-kpi-label">' + escape(label) +
    '</div><div class="apl-kpi-value">' + escape(value) + '</div></div>'
    for label, value in kpi_items
)
st.markdown('''<style>
.apl-kpi-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0 14px}
.apl-kpi {border:1px solid #334155;border-radius:14px;background:rgba(100,116,139,.08);padding:16px;min-width:0}
.apl-kpi-label {font-size:.88rem;color:inherit;opacity:.82;margin-bottom:7px}
.apl-kpi-value {font-size:clamp(1.35rem,2.2vw,2rem);font-weight:650;line-height:1.2;white-space:nowrap;font-variant-numeric:tabular-nums}
@media(min-width:1500px){.apl-kpi-grid{grid-template-columns:repeat(6,minmax(0,1fr))}.apl-kpi-value{font-size:clamp(1.15rem,1.5vw,1.8rem)}}
@media(max-width:750px){.apl-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="apl-kpi-grid">' + kpi_html + '</div>', unsafe_allow_html=True)
st.caption('Financial KPI amounts are in CU (unverified currency units); K = thousand, M = million.  Dataset is treated as transaction lines, not unique orders. No claim of corporate affiliation or audited financials.')
tabs=st.tabs(['Executive overview','Customer value','Product & category','Discount lab','Market intelligence','Operations linkage','Data audit & decisions'])
with tabs[0]:
    st.subheader('Profitability performance')
    a,b=st.columns(2)
    with a:bars(aggregate(d,'Market'),'Market','profit','Recorded profit by market')
    with b:bars(aggregate(d,'Customer Segment'),'Customer Segment','revenue','Net revenue by customer segment')
    cats=aggregate(d,'Category Name').sort_values('profit')
    st.markdown('#### Portfolio concentration & exposure')
    st.info(
        f"**Executive insight:** {m['loss_lines']:,} transaction lines are loss-making, "
        f"representing {100*m['loss_lines']/m['lines']:.1f}% of the filtered population. "
        "Prioritize loss concentration and validate underlying contracts before changing prices."
    )
    a,b,c=st.columns(3)
    a.metric('Gross-to-net discount rate',f"{100*m['discount']/m['gross']:.2f}%")
    b.metric('Observed loss magnitude',money(m['loss_amount']))
    c.metric('Late delivery risk flag',f"{m['late_rate_pct']:.1f}%")
    show_table(cats[['Category Name','revenue','profit','margin_pct','discount_pct','loss_lines']].sort_values('profit'))
    dl(cats,'executive_category_summary')
with tabs[1]:
    cust=customer_table(d)
    st.subheader('Customer contribution and margin quality')
    a,b=st.columns(2)
    with a:bars(cust,'Customer Id','profit','Top customer profit',15)
    with b:bars(cust[cust.profit < 0],'Customer Id','profit','Most loss-making customers',15,ranking='bottom')
    st.plotly_chart(px.scatter(cust.assign(customer_label=cust['Customer Id'].astype(str)),x='revenue',y='margin_pct',size='lines',color='tier',hover_data=['customer_label','profit'],title='Customer revenue versus profit margin',labels={'revenue':'Net revenue (CU)','margin_pct':'Profit margin (%)','customer_label':'Customer ID'}),width="stretch")
    show_table(cust.sort_values('profit'))
    dl(cust,'customer_value_export')
    st.caption('Customer tiers describe observed contribution in the selected data only; they do not estimate customer lifetime value.')
with tabs[2]:
    cat=aggregate(d,'Category Name');prod=aggregate(d,'Product Name')
    a,b=st.columns(2)
    with a:bars(cat,'Category Name','profit','Most profitable categories')
    with b:bars(prod,'Product Name','profit','Most profitable products')
    high=prod.revenue.quantile(.75);weak=prod[(prod.revenue>=high)&(prod.margin_pct<m['margin_pct'])].sort_values('revenue',ascending=False)
    st.markdown('#### High-revenue, below-portfolio-margin products')
    show_table(weak)
    heat=aggregate(d,['Market','Category Name'])
    piv=heat.pivot(index='Category Name',columns='Market',values='margin_pct')
    st.plotly_chart(px.imshow(piv,aspect='auto',color_continuous_scale='RdYlGn',color_continuous_midpoint=0,title='Category margin by market (%)'),width="stretch")
    dl(prod,'product_profitability_export')
with tabs[3]:
    st.subheader('Observed discount exposure')
    bands=discount_bands(d)
    st.plotly_chart(px.bar(bands,x='Discount band',y='margin_pct',title='Observed weighted margin by discount band (association, not causation)'),width="stretch")
    show_table(bands)
    st.markdown('#### Mechanical scenario simulator')
    delta=st.slider('Discount adjustment (percentage points)',-20,20,0,1)
    s=scenario(d,delta)
    a,b,c=st.columns(3)
    a.metric('Scenario net revenue',money(s['revenue']),money(s['revenue']-m['revenue']))
    b.metric('Scenario profit',money(s['profit']),money(s['delta_profit']))
    c.metric('Scenario margin',f"{s['margin_pct']:.2f}%")
    steps=pd.DataFrame([{'Discount change (pp)':i,**scenario(d,i)} for i in range(-20,21,2)])
    st.plotly_chart(px.line(steps,x='Discount change (pp)',y='profit',markers=True,title='Mechanical sensitivity: recorded profit vs discount adjustment'),width="stretch")
    st.warning('Not a forecast. Holds unit volumes, costs and order mix constant; discount dollars capped at 0–100% of gross sales. Does not infer price elasticity or prove discount causation.')
    dl(steps,'discount_sensitivity')
with tabs[4]:
    for level in ['Market','Order Region','Order Country']:
        st.markdown('#### '+level)
        t=aggregate(d,level)
        a,b=st.columns([1.25,1])
        with a:bars(t,level,'profit',f'Profit by {level}',20)
        with b:show_table(t.sort_values('profit'))
        dl(t,'geography_'+level.lower().replace(' ','_'))
with tabs[5]:
    st.subheader('Shipping service and commercial outcomes')
    mode=aggregate(d,'Shipping Mode');a,b=st.columns(2)
    with a:bars(mode,'Shipping Mode','margin_pct','Margin by shipping mode')
    with b:bars(mode,'Shipping Mode','late_rate','Late-risk flag by shipping mode')
    show_table(mode)
    st.info('Shipping charges and shipment-level identifiers are absent. Shipping mode comparisons are descriptive; no shipping-cost attribution or causal claims are made.')
with tabs[6]:
    st.subheader('Reconciliation and transparency')
    st.write('Original source rows:',len(raw),' | Valid rows:',len(raw_valid),' | Current filtered rows:',len(d))
    audit=pd.DataFrame({'Check':['Missing key financial values','Nonpositive gross or net sales','Negative discounts','Gross − discount − net discrepancy > 0.05','Profit field mismatch > 0.01','Duplicate full source rows'], 'Count':[int(raw[['gross_sales','discount','net_sales','profit']].isna().any(axis=1).sum()),int(((raw.gross_sales<=0)|(raw.net_sales<=0)).sum()),int((raw.discount<0).sum()),int((raw.reconciliation_error.abs()>.05).sum()),int(((pd.to_numeric(raw['Benefit per order'],errors='coerce')-raw.profit).abs()>.01).sum()),int(raw.duplicated(subset=[c for c in raw.columns if c not in ['gross_sales','discount','net_sales','profit','reconciliation_error','valid_financial','loss_line','late_flag','margin_pct']]).sum())]})
    show_table(audit)
    st.write('Filtered gross minus discount minus net sales:',f"{m['gross']-m['discount']-m['revenue']:,.2f} CU (rounding tolerance applies)")
    st.markdown('#### Prioritized diagnostic opportunities')
    cat=aggregate(d,'Category Name');losers=cat[cat.profit<0].sort_values('profit')
    if len(losers):st.error(f'{len(losers)} categories have negative aggregate recorded profit. Review product economics and commercial terms before intervention.')
    else:st.success('No category has negative aggregate recorded profit in this selection.')
    customers=customer_table(d);st.write(f"{int((customers.profit<0).sum()):,} customers have negative observed aggregate profit in this selection.")
    st.markdown('#### Highest-loss products for commercial review')
    product_losses = aggregate(d, 'Product Name')
    product_losses = product_losses.loc[product_losses.profit < 0].sort_values('profit')
    if len(product_losses):
        show_table(product_losses.head(15))
        dl(product_losses, 'loss_making_products')
    else:
        st.success('No products have negative aggregate recorded profit in this selection.')
    st.markdown('**Decision protocol:** validate transactions → identify concentrated loss exposure → review cost/pricing contracts → pilot a controlled change → monitor realized margin and retention.')
    st.caption('Dataset has no timestamp, currency definition, shipping cost, complete cost ledger, or causal experiment. A temporal trend, cost-based attribution, true customer lifetime value, and forecast would be misleading.')
    dl(audit,'financial_quality_audit')
