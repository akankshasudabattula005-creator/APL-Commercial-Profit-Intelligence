# Commercial Profit Intelligence — Public Demonstration

**Live dashboard:** https://apl-commercial-profit-intelligence.streamlit.app/  
**GitHub repository:** https://github.com/akankshasudabattula005-creator/APL-Commercial-Profit-Intelligence

## Overview
An independently developed, interactive supply-chain commercial analytics prototype using **16,000 fully synthetic transaction lines**. The demo is not affiliated with, audited by, or endorsed by APL Logistics / KWE Group. Its figures are generated examples, **not company financial results**.

## Implemented dashboard
Seven sections: **Executive overview**, **Customer value**, **Product & category**, **Discount lab**, **Market intelligence**, **Operations linkage**, **Data audit & decisions**. Shared filters: market, order region, customer segment, category, product and shipping mode. The interface supports CSV exports and a bounded discount what-if calculator.

## Public deliverables
- `app.py`: seven-section Streamlit dashboard and source selection
- `analytics.py`: auditable preparation, reconciliation, aggregation, customer tiers, scenarios
- `ui_helpers.py`: chart and numeric formatting helpers
- `generate_demo_data.py`: deterministic synthetic data generator
- `data/APL_Logistics.csv`: **synthetic** generated dataset (16,000 lines)
- `tests/`: automated analytics, helper and full dashboard smoke tests
- `reports/Research_Report.pdf`: synthetic demonstration research report
- `reports/Executive_Brief.pdf`: synthetic demonstration executive summary

## Run and test
```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```
Optional: `python generate_demo_data.py` regenerates the synthetic CSV. The application reads its bundled CSV using a content-dependent cache key, preventing an older same-named CSV from being silently reused after deployment.

## Financial methodology
- Gross sales = `Sales`; discount = `Order Item Discount`; net sales = `Order Item Total`; recorded synthetic profit = `Order Profit Per Order`.
- Weighted net margin = 100 × SUM(profit) / SUM(net sales).
- Financial rows require complete financial values, positive gross and net, nonnegative discount and absolute reconciliation discrepancy ≤ 0.05 CU.
- Discount slider = mechanical fixed-volume accounting sensitivity, not a causal forecast.
- Customer tiers = descriptive contribution groups, not customer lifetime value predictions.
- Shipping mode associations do not establish actual shipping-cost leakage or causal effects.
- Financial values use **CU (unspecified currency units)**. Lines are not necessarily unique orders.

## Data safety
The public CSV is synthetic and contains no original company records, names, street addresses, or precise coordinates. User-uploaded CSVs are processed in the active app session and are not intentionally written to the repository; users should upload only data they are authorized to process. The publicly available reports describe **synthetic demo outcomes** only.

## Limitations
This educational prototype does not prove real-world performance, corporate affiliation, verified financial impact, price elasticity, causal discount thresholds, or customer lifetime value. The original provider dataset and original private analysis are deliberately excluded from this public repository.

## Deployment and submission
Streamlit Community Cloud should point to this repository's `main` branch and entrypoint `app.py`. Verify that the **Data audit & decisions** tab shows **16,000 source rows** in a new private browser session, all seven tabs render, and no red errors are present. Submit the **repository root URL**, not `/settings`, and the **live Streamlit URL**. Include both PDFs if the evaluation portal requests reports.
