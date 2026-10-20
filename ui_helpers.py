"""Pure formatting and chart-data helpers, independently testable."""
import pandas as pd

def compact_number(value):
    value = float(value)
    prefix = '-' if value < 0 else ''
    magnitude = abs(value)
    if magnitude >= 1_000_000_000: return f'{prefix}{magnitude / 1_000_000_000:,.2f}B'
    if magnitude >= 1_000_000: return f'{prefix}{magnitude / 1_000_000:,.2f}M'
    if magnitude >= 10_000: return f'{prefix}{magnitude / 1_000:,.1f}K'
    return f'{prefix}{magnitude:,.0f}'

def chart_category_labels(values):
    """Treat customer IDs and all other labels as categories."""
    return pd.Series(values, index=values.index).fillna('Unknown').astype(str)

def customer_rankings(frame, n=15):
    """Return true highest-profit and most-negative-profit customers."""
    return frame.nlargest(n, 'profit').copy(), frame[frame['profit'] < 0].nsmallest(n, 'profit').copy()
