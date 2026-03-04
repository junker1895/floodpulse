# FloodPulse

FloodPulse is a public-facing flood awareness app with a Windy-inspired UX for river level trends and risk signals.

## Stack
- Frontend: Vite + React + TypeScript + Leaflet
- Backend: FastAPI + Postgres/PostGIS
- Ingestion: polling collector every 10 minutes

## Run locally
```bash
docker compose up --build
```
Then open: http://localhost:5173

## Services
- `db`: PostGIS database
- `api`: FastAPI app at http://localhost:8000
- `collector`: runs `python -m backend.collector.poller`
- `frontend`: Vite dev server

## Seeding and data
Seed command:
```bash
python -m backend.seed
```

Static data lives in `/data`:
- `rivers.geojson`
- `gauges.csv`
- `mock_observations_seed.json`

To add gauges: edit `data/gauges.csv` and rerun seed.

## Providers
Provider interface lives in `backend/providers`.
- `mock_provider.py` (default, keyless): reads `data/mock_observations_seed.json` and generates changing values.
- `bom_provider.py`: placeholder for real integration.

Set provider via `.env`:
```env
PROVIDER=mock
```

## API
- `GET /health`
- `GET /api/gauges?q=&bbox=minLon,minLat,maxLon,maxLat&rising_fast_only=true`
- `GET /api/gauges/{gauge_id}/timeseries?var=level_m&hours=168`
- `GET /api/rivers`

## Production frontend build
```bash
cd frontend
npm ci
npm run build
```

## Disclaimer
Informational only; not an official forecast.
