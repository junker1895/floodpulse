from backend.db import get_cursor


def ensure_schema() -> None:
    with get_cursor() as (_, cur):
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS gauges (
                gauge_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                state TEXT,
                river_name TEXT,
                geom geometry(Point, 4326) NOT NULL,
                provider TEXT NOT NULL,
                external_id TEXT,
                is_active BOOLEAN NOT NULL DEFAULT TRUE
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS rivers (
                river_id TEXT PRIMARY KEY,
                name TEXT,
                geom geometry(LineString, 4326) NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS observations (
                id BIGSERIAL PRIMARY KEY,
                gauge_id TEXT REFERENCES gauges(gauge_id),
                var TEXT NOT NULL,
                observed_at TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                units TEXT,
                quality TEXT,
                source TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_obs_gauge_var_time ON observations(gauge_id, var, observed_at DESC);
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS latest_observations (
                gauge_id TEXT REFERENCES gauges(gauge_id),
                var TEXT NOT NULL,
                observed_at TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                units TEXT,
                trend TEXT NOT NULL,
                rate_per_hr DOUBLE PRECISION,
                severity TEXT NOT NULL,
                source TEXT,
                PRIMARY KEY (gauge_id, var)
            );
            """
        )
