import csv
import json
from pathlib import Path
from backend.db import get_cursor
from backend.schema import ensure_schema

DATA_DIR = Path('/data') if Path('/data').exists() else Path(__file__).resolve().parents[2] / 'data'


def seed_rivers(cur):
    rivers_path = DATA_DIR / 'rivers.geojson'
    geo = json.loads(rivers_path.read_text())
    for feat in geo['features']:
        rid = feat['properties']['river_id']
        name = feat['properties'].get('name', rid)
        coords = feat['geometry']['coordinates']
        linestring = 'LINESTRING(' + ','.join(f"{x} {y}" for x, y in coords) + ')'
        cur.execute(
            """
            INSERT INTO rivers (river_id, name, geom)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326))
            ON CONFLICT (river_id) DO UPDATE SET name=EXCLUDED.name, geom=EXCLUDED.geom;
            """,
            (rid, name, linestring),
        )


def seed_gauges(cur):
    gauges_path = DATA_DIR / 'gauges.csv'
    with gauges_path.open() as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            cur.execute(
                """
                INSERT INTO gauges (gauge_id, name, state, river_name, geom, provider, external_id, is_active)
                VALUES (%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),4326),%s,%s,%s)
                ON CONFLICT (gauge_id) DO UPDATE SET
                    name=EXCLUDED.name,
                    state=EXCLUDED.state,
                    river_name=EXCLUDED.river_name,
                    geom=EXCLUDED.geom,
                    provider=EXCLUDED.provider,
                    external_id=EXCLUDED.external_id,
                    is_active=EXCLUDED.is_active;
                """,
                (
                    row['gauge_id'], row['name'], row['state'], row.get('river_name'),
                    row['lon'], row['lat'], row.get('provider', 'mock'), row.get('external_id', row['gauge_id']),
                    row.get('is_active', 'true').lower() == 'true',
                ),
            )


def run():
    ensure_schema()
    with get_cursor() as (_, cur):
        seed_rivers(cur)
        seed_gauges(cur)


if __name__ == '__main__':
    run()
