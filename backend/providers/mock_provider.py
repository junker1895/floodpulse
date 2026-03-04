import json
import math
from datetime import datetime, timezone
from pathlib import Path
from backend.providers.base import ProviderObservation

DATA_DIR = Path('/data') if Path('/data').exists() else Path(__file__).resolve().parents[3] / 'data'


class MockProvider:
    def __init__(self) -> None:
        self.seed = json.loads((DATA_DIR / 'mock_observations_seed.json').read_text())

    def fetch_observations(self) -> list[ProviderObservation]:
        now = datetime.now(timezone.utc)
        out: list[ProviderObservation] = []
        for item in self.seed:
            phase = (now.timestamp() / 3600.0) + item.get('phase', 0)
            variation = math.sin(phase) * item.get('amplitude', 0.1)
            drift = math.sin(phase / 6) * item.get('drift', 0.08)
            value = round(item['base_value'] + variation + drift, 3)
            out.append(
                ProviderObservation(
                    gauge_id=item['gauge_id'],
                    var=item.get('var', 'level_m'),
                    observed_at=now,
                    value=value,
                    units=item.get('units', 'm'),
                    quality='good',
                    source='mock_provider',
                )
            )
        return out
