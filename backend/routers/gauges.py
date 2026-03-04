from fastapi import APIRouter, Query
from backend.db import get_cursor

router = APIRouter(prefix='/api')


@router.get('/gauges')
def list_gauges(q: str | None = None, bbox: str | None = None, rising_fast_only: bool = False):
    wheres = ["g.is_active=true"]
    params: list = []
    if q:
        wheres.append("(g.name ILIKE %s OR g.gauge_id ILIKE %s)")
        params += [f"%{q}%", f"%{q}%"]
    if bbox:
        min_lon, min_lat, max_lon, max_lat = [float(v) for v in bbox.split(',')]
        wheres.append("ST_Intersects(g.geom, ST_MakeEnvelope(%s,%s,%s,%s,4326))")
        params += [min_lon, min_lat, max_lon, max_lat]
    if rising_fast_only:
        wheres.append("COALESCE(lo.severity, 'normal')='rising_fast'")

    sql = f"""
    SELECT g.gauge_id, g.name, g.state, g.river_name, g.provider, g.external_id,
           ST_Y(g.geom) as lat, ST_X(g.geom) as lon,
           lo.observed_at, lo.value, lo.units, lo.trend, lo.rate_per_hr, lo.severity, lo.source
    FROM gauges g
    LEFT JOIN latest_observations lo ON lo.gauge_id=g.gauge_id AND lo.var='level_m'
    WHERE {' AND '.join(wheres)}
    ORDER BY g.name;
    """
    with get_cursor(dict_cursor=True) as (_, cur):
        cur.execute(sql, params)
        return cur.fetchall()


@router.get('/gauges/{gauge_id}/timeseries')
def timeseries(gauge_id: str, var: str = 'level_m', hours: int = Query(default=168, le=24 * 30)):
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT observed_at, value FROM observations
            WHERE gauge_id=%s AND var=%s AND observed_at >= now() - (%s || ' hours')::interval
            ORDER BY observed_at ASC;
            """,
            (gauge_id, var, hours),
        )
        return [{'t': row[0], 'value': row[1]} for row in cur.fetchall()]
