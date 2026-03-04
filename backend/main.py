from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.gauges import router as gauges_router
from backend.routers.rivers import router as rivers_router
from backend.schema import ensure_schema
from backend.seed import run as seed_run

app = FastAPI(title='FloodPulse API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup():
    try:
        ensure_schema()
        seed_run()
    except Exception:
        # allows app startup for local unit tests without a running DB
        pass


@app.get('/health')
def health():
    return {'status': 'ok'}


app.include_router(gauges_router)
app.include_router(rivers_router)
