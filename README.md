# Commercial Profit Intelligence — Supply Chain Case Study

A reproducible, line-level profitability decision-support application built with Python, Pandas, Plotly and Streamlit.

**Important:** This is an educational case study using the provided APL-labelled dataset. It is **not** an official APL Logistics or KWE Group product, audit or endorsed financial report. Monetary values are shown in **currency units (CU)** because the dataset does not independently establish currency.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

Open the localhost URL shown by Streamlit. Dataset is bundled at `data/APL_Logistics.csv`. An alternative CSV can be uploaded in the sidebar.

## Modules
Executive overview; customer value; product and category; observed discount exposure and scenario lab; geographic profitability; shipping-mode association; data audit and decision protocol. All visuals share sidebar filters; analytical tables export as CSV.

## Financial definitions
- `gross_sales = Sales` (pre-discount line sales).
- `discount = Order Item Discount` (line discount amount).
- `net_sales = Order Item Total` (after-discount line sales).
- `profit = Order Profit Per Order` (recorded profit field; treated as line-level profit).
- `weighted_margin = SUM(profit) / SUM(net_sales)` (not mean of individual margin percentages).
- `discount_rate = SUM(discount) / SUM(gross_sales)`.
- Reconciliation: `ABS(gross_sales - discount - net_sales) <= 0.05` per line, with positive gross/net sales and nonnegative discount. Excluded rows are counted in the audit tab.
- Loss-making customer: negative aggregate profit for customer ID in the current selection. Tiers are descriptive, not CLV predictions.

## Interpretation limitations
No date/time, transaction currency metadata, shipment costs, complete cost accounting, unique order ID, customer acquisition costs, or randomized discount experiment. Do not claim temporal trends, causal discount thresholds, actual shipping-cost leakage, or customer lifetime value. The discount slider is a **static accounting sensitivity**, assuming fixed quantities, costs and mix. Changing price may change demand in reality.

## Deployment (Streamlit Community Cloud)
1. Create a **public** GitHub repository, push the project including `app.py`, `analytics.py`, `requirements.txt`, `tests/`, and `data/` (confirm dataset sharing is permitted).
2. Open https://share.streamlit.io/ and connect your GitHub repository. Entry point: `app.py`.
3. Verify every tab, sidebar filter, download, upload, and first-run behavior in an incognito browser.
4. Submit the **repository root URL**, e.g. `https://github.com/USER/REPO`, **not** a `/settings/...` URL.
5. Submit the actual live `https://...streamlit.app/` URL after verification. Never claim deployment before testing it.

## Submission checklist
- [ ] `python -m pytest -q` passes
- [ ] `streamlit run app.py` opens locally
- [ ] Data-sharing rights confirmed
- [ ] Public repository URL opens while logged out
- [ ] Streamlit deployment opens while logged out
- [ ] Research report and executive brief included
- [ ] No claims of verified company affiliation or invented financial forecasts


## UI refinement update (October 2026)

- Replaced deprecated `use_container_width=True` with `width="stretch"`.
- Added compact KPI formatting (K/M/B currency units).
- Formatted financial tables and highlighted negative profit and margins.
- Added executive loss-line exposure narrative and a loss-making product review table.
- Set `observed=False` explicitly in pandas aggregation to preserve prior behavior.

### Windows quick start

```powershell
cd "D:\APL_Profit_Intelligence_Refined"
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Financial amounts are expressed in unverified currency units (CU). The scenario calculator is a fixed-volume mechanical sensitivity, not a forecast.

## Final presentation refinements

- Responsive HTML KPI grid prevents numeric truncation and keeps CU in the unit legend.
- Customer IDs are categorical in horizontal profit ranking charts.
- Loss-making customer ranking includes only negative-profit customers.
- Added isolated regression tests for KPI formatting and customer rankings.
- This is an independent dataset case study, not audited APL Logistics corporate financials.
