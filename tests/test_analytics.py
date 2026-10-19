import pandas as pd
import pytest
from analytics import prepare,metrics,aggregate,scenario
@pytest.fixture
def data():
    return prepare(pd.DataFrame({'Sales':[100.,200.],'Order Item Discount':[10.,20.],'Order Item Total':[90.,180.],'Order Profit Per Order':[5.,-10.],'Benefit per order':[5.,-10.],'Order Item Discount Rate':[.1,.1],'Order Item Quantity':[1,2],'Days for shipping (real)':[3,5],'Days for shipment (scheduled)':[3,4],'Customer Segment':['A','B'],'Market':['X','Y'],'Order Region':['R','R'],'Order Country':['C','C'],'Category Name':['P','P'],'Product Name':['A','B'],'Shipping Mode':['S','S'],'Customer Id':[1,2],'Late_delivery_risk':[0,1]}))
def test_reconcile(data):assert data.valid_financial.all()
def test_metrics(data):
    m=metrics(data);assert m['revenue']==270;assert m['profit']==-5;assert m['loss_lines']==1
def test_aggregation(data):assert aggregate(data,'Category Name').iloc[0]['margin_pct']==pytest.approx(-5/270*100)
def test_scenario_zero(data):assert scenario(data,0)['profit']==-5
def test_scenario_increase(data):assert scenario(data,10)['profit']==pytest.approx(-35)
def test_scenario_decrease(data):assert scenario(data,-10)['profit']==pytest.approx(25)
def test_invalid_financial(data):
    d=data.copy();d.loc[0,'valid_financial']=False;assert (~d.valid_financial).sum()==1
def test_empty_metrics(data):assert metrics(data.iloc[:0])['revenue']==0
