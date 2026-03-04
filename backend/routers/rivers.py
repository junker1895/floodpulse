from fastapi import APIRouter
from backend.db import get_cursor

router = APIRouter(prefix='/api')


@router.get('/rivers')
def rivers():
    with get_cursor() as (_, cur):
        cur.execute(
            """
            SELECT json_build_object(
                'type','FeatureCollection',
                'features', COALESCE(json_agg(json_build_object(
                    'type','Feature',
                    'properties', json_build_object('river_id', river_id, 'name', name),
                    'geometry', ST_AsGeoJSON(geom)::json
                )), '[]'::json)
            )
            FROM rivers;
            """
        )
        return cur.fetchone()[0]
