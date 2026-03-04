import time
from datetime import timedelta
from backend.config import settings
from backend.db import get_cursor
from backend.providers.factory import get_provider
from backend.schema import ensure_schema
from backend.seed import run as seed_run


def compute_trend(latest: float, prev: float, eps: float) -> str:
    delta = latest - prev
    if delta > eps:
        return 'up'
    if delta < -eps:
        return 'down'
    return 'steady'


def poll_once():
    ensure_schema()
    seed_run()
    provider = get_provider()
    observations = provider.fetch_observations()
    with get_cursor() as (_, cur):
        for obs in observations:
            cur.execute(
                """
                INSERT INTO observations (gauge_id,var,observed_at,value,units,quality,source)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                """,
                (obs['gauge_id'], obs['var'], obs['observed_at'], obs['value'], obs['units'], obs['quality'], obs['source']),
            )
            cur.execute(
                """
                SELECT value, observed_at FROM observations
                WHERE gauge_id=%s AND var=%s AND observed_at <= %s - interval '50 minutes'
                ORDER BY ABS(EXTRACT(EPOCH FROM (observed_at - (%s - interval '60 minutes')))) ASC
                LIMIT 1;
                """,
                (obs['gauge_id'], obs['var'], obs['observed_at'], obs['observed_at']),
            )
            prev = cur.fetchone()
            if prev:
                prev_val, prev_at = prev
                hours = max((obs['observed_at'] - prev_at).total_seconds() / 3600.0, 1e-6)
                rate = (obs['value'] - prev_val) / hours
            else:
                rate = 0.0
                prev_val = obs['value']
            trend = compute_trend(obs['value'], prev_val, settings.trend_epsilon_level)
            severity = 'rising_fast' if rate >= settings.rising_fast_threshold_level_per_hr else 'normal'
            if rate <= -settings.rising_fast_threshold_level_per_hr:
                severity = 'falling_fast'
            cur.execute(
                """
                INSERT INTO latest_observations (gauge_id,var,observed_at,value,units,trend,rate_per_hr,severity,source)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (gauge_id,var) DO UPDATE SET
                  observed_at=EXCLUDED.observed_at,
                  value=EXCLUDED.value,
                  units=EXCLUDED.units,
                  trend=EXCLUDED.trend,
                  rate_per_hr=EXCLUDED.rate_per_hr,
                  severity=EXCLUDED.severity,
                  source=EXCLUDED.source;
                """,
                (obs['gauge_id'], obs['var'], obs['observed_at'], obs['value'], obs['units'], trend, rate, severity, obs['source']),
            )


def main():
    while True:
        poll_once()
        time.sleep(settings.poll_interval_seconds)


if __name__ == '__main__':
    main()
