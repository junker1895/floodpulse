from contextlib import contextmanager
from fastapi.testclient import TestClient
from backend.main import app


def test_health():
    client = TestClient(app)
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_gauges(monkeypatch):
    from backend.routers import gauges

    class FakeCur:
        def execute(self, sql, params):
            self._rows = [
                {
                    'gauge_id': 'g-1', 'name': 'Brisbane', 'state': 'QLD', 'river_name': 'Brisbane River',
                    'provider': 'mock', 'external_id': 'g-1', 'lat': -27.4, 'lon': 153.0,
                    'observed_at': None, 'value': 2.0, 'units': 'm', 'trend': 'up', 'rate_per_hr': 0.1,
                    'severity': 'rising_fast', 'source': 'mock_provider'
                }
            ]

        def fetchall(self):
            return self._rows

    @contextmanager
    def fake_cursor(dict_cursor=False):
        yield None, FakeCur()

    monkeypatch.setattr(gauges, 'get_cursor', fake_cursor)
    client = TestClient(app)
    res = client.get('/api/gauges')
    assert res.status_code == 200
    assert res.json()[0]['gauge_id'] == 'g-1'
