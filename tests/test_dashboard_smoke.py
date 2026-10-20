"""Smoke-test the entire seven-tab dashboard without a running Streamlit server.

Uses a minimal Streamlit stand-in so plot construction, data access and
branch execution are checked by pytest even in CI environments.
"""
import runpy
import sys
import types
from pathlib import Path

class StreamlitStandIn(types.ModuleType):
    def __init__(self):
        super().__init__('streamlit')
        self.sidebar = self
        self.charts = 0
        self.tables = 0
        self.tabs_seen = []
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def cache_data(self, **kwargs): return lambda f: f
    def columns(self, spec): return [self] * (spec if isinstance(spec, int) else len(spec))
    def tabs(self, labels):
        self.tabs_seen = labels
        return [self] * len(labels)
    def radio(self, label, options, **kwargs): return options[0]
    def multiselect(self, *args, **kwargs): return []
    def slider(self, *args, **kwargs): return 0
    def plotly_chart(self, fig, **kwargs):
        assert fig is not None
        self.charts += 1
    def dataframe(self, df, **kwargs):
        assert df is not None
        self.tables += 1
    def download_button(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def stop(self): raise RuntimeError('Unexpected stop() in synthetic dataset')
    def __getattr__(self, name):
        if name.startswith('__'): raise AttributeError(name)
        return lambda *args, **kwargs: None


def test_seven_tab_dashboard_smoke(monkeypatch):
    fake = StreamlitStandIn()
    monkeypatch.setitem(sys.modules, 'streamlit', fake)
    path = Path(__file__).resolve().parents[1] / 'app.py'
    runpy.run_path(str(path), run_name='__main__')
    assert len(fake.tabs_seen) == 7
    assert fake.charts >= 10
    assert fake.tables >= 5
