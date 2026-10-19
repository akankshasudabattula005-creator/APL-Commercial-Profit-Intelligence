import pandas as pd
from ui_helpers import compact_number, chart_category_labels, customer_rankings

def test_compact_values():
    assert compact_number(33050000) == '33.05M'
    assert compact_number(3970000) == '3.97M'
    assert compact_number(-3883547) == '-3.88M'

def test_customer_ids_are_categorical():
    x = pd.Series([1428, 14086, 18109])
    assert chart_category_labels(x).tolist() == ['1428', '14086', '18109']

def test_rankings_exclude_positive_profit_from_loss_chart():
    t = pd.DataFrame({'Customer Id':[10,20,30,40], 'profit':[100,-20,-50,200]})
    top, bottom = customer_rankings(t, 2)
    assert top['Customer Id'].tolist() == [40,10]
    assert bottom['Customer Id'].tolist() == [30,20]
