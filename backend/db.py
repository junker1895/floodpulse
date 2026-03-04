from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from backend.config import settings


def get_connection():
    return psycopg2.connect(settings.dsn)


@contextmanager
def get_cursor(dict_cursor: bool = False):
    conn = get_connection()
    cursor_factory = RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_factory)
    try:
        yield conn, cur
        conn.commit()
    finally:
        cur.close()
        conn.close()
