"""Create wholly synthetic, deterministic transaction lines. No company records used."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(20261019)
n = 16000
categories = {
    'Accessories': ['Demo Backpack', 'Demo Water Bottle', 'Demo Travel Kit'],
    'Footwear': ['Demo Running Shoe', 'Demo Trail Shoe'],
    'Apparel': ['Demo Training Shirt', 'Demo Jacket'],
    'Electronics': ['Demo Fitness Tracker', 'Demo Headphones'],
    'Equipment': ['Demo Exercise Mat', 'Demo Training Ball'],
}
cat = rng.choice(list(categories), size=n, p=[.24,.22,.21,.16,.17])
prod = [rng.choice(categories[c]) for c in cat]
base_prices = {p: (20 + 16*j + 10*i) for i,ps in enumerate(categories.values()) for j,p in enumerate(ps)}
unit_price = np.array([base_prices[p] for p in prod], dtype=float)
qty = rng.integers(1, 6, size=n)
gross = np.round(unit_price * qty, 2)
disc_rate = rng.choice([0,.03,.05,.08,.10,.15,.20,.25,.35], size=n, p=[.25,.08,.12,.12,.12,.12,.09,.07,.03])
discount = np.round(gross*disc_rate,2)
net = np.round(gross-discount,2)
market = rng.choice(['Europe','Pacific Asia','USCA','LATAM','Africa'], size=n)
region_lookup = {'Europe':['Western Europe','Northern Europe'], 'Pacific Asia':['South Asia','Southeast Asia'], 'USCA':['US Center','US East'], 'LATAM':['South America','Central America'], 'Africa':['North Africa','West Africa']}
region = [rng.choice(region_lookup[m]) for m in market]
country_lookup = {'Europe':'France','Pacific Asia':'India','USCA':'United States','LATAM':'Brazil','Africa':'South Africa'}
country = [country_lookup[m] for m in market]
ship = rng.choice(['Standard Class','Second Class','First Class','Same Day'], size=n, p=[.55,.22,.18,.05])
segment = rng.choice(['Consumer','Corporate','Home Office'], size=n, p=[.52,.31,.17])
customer = rng.integers(1, 2401, size=n)
planned = np.where(ship=='Same Day',0,np.where(ship=='First Class',2,np.where(ship=='Second Class',3,5)))
actual = np.maximum(0, planned+rng.choice([-1,0,1,2,3], size=n,p=[.12,.40,.28,.15,.05]))
late = (actual>planned).astype(int)
# Synthetic unit economics: controlled segment, shipping, discount and random variation.
base_cost = gross * rng.uniform(.64,.84,size=n)
shipping_cost = np.where(ship=='Same Day',18,np.where(ship=='First Class',11,np.where(ship=='Second Class',7,4)))
profit = np.round(net-base_cost-shipping_cost+rng.normal(0,6,size=n),2)
rows = pd.DataFrame({
    'Type':rng.choice(['DEBIT','CREDIT','TRANSFER'],size=n),
    'Days for shipping (real)':actual,
    'Days for shipment (scheduled)':planned,
    'Benefit per order':profit,
    'Sales per customer':net,
    'Delivery Status':np.where(late==1,'Late delivery','Shipping on time'),
    'Late_delivery_risk':late,
    'Category Id':pd.Categorical(cat).codes+1,
    'Category Name':cat,
    'Customer City':['Synthetic City']*n,
    'Customer Country':['Synthetic Country']*n,
    'Customer Id':customer,
    'Customer Segment':segment,
    'Customer State':['Synthetic State']*n,
    'Department Id':pd.Categorical(cat).codes+1,
    'Department Name':cat,
    'Market':market,
    'Order City':['Synthetic Order City']*n,
    'Order Country':country,
    'Order Customer Id':customer,
    'Order Item Discount':discount,
    'Order Item Discount Rate':disc_rate,
    'Order Item Product Price':unit_price,
    'Order Item Profit Ratio':np.round(profit/net,5),
    'Order Item Quantity':qty,
    'Sales':gross,
    'Order Item Total':net,
    'Order Profit Per Order':profit,
    'Order Region':region,
    'Order State':['Synthetic Region']*n,
    'Order Status':['COMPLETE']*n,
    'Product Name':prod,
    'Product Price':unit_price,
    'Shipping Mode':ship,
})
out = Path(__file__).parent/'data'/'APL_Logistics.csv'
out.parent.mkdir(parents=True,exist_ok=True)
rows.to_csv(out,index=False)
print(f'Created {len(rows):,} synthetic lines at {out}')
