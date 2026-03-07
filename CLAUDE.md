# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FloodWatch is a single-file HTML/JS/CSS app — a flood monitoring dashboard for Australia. There is no build system, package manager, or backend. Real data comes from Open-Meteo and RainViewer APIs.

## Development

Open `index.html` directly in a browser. No build step required.

## Architecture

Everything lives in `index.html`:

- **CSS** (`:root` vars → component styles) — dark theme using CSS custom properties; `--low` (green), `--mid` (yellow), `--high` (red) are the risk color tokens used throughout
- **Map** — MapLibre GL 4.7.1 with CartoDB Dark raster basemap tiles
- **Rivers** — PMTiles vector layer (`rivers.pmtiles` on Cloudflare R2, HydroRIVERS dataset). Protocol registered via `maplibregl.addProtocol('pmtiles', ...)`. Layer `rivers-base` uses `ORD_FLOW` attribute + zoom interpolation to set `line-width` and `line-opacity`
- **Flood zones** — GeoJSON `circle` layers (5 hardcoded zones, styled by high/mid/low risk)
- **Gauge markers** — GeoJSON `circle` + `symbol` layers (not HTML markers). Data fetched from Open-Meteo Flood API
- **Rain canvas** — `<canvas id="rainCanvas">` overlaid on the map, animated via `requestAnimationFrame` with 80 simulated drops. Toggled alongside the radar layer
- **Sidebar** — verdict card, gauge list, alert cards, and timeline bars all built dynamically via JS; sparkline drawn on `<canvas id="spark">` by `drawSparkline(data)`
- **Live data** — Open-Meteo Flood API (discharge m³/s), Open-Meteo Weather API (hourly rainfall), RainViewer (animated radar frames). All refreshed every 10 minutes via `setInterval`

## Key Patterns

- Risk level (`high`/`mid`/`low`) drives CSS class names, MapLibre paint properties, and sidebar colors
- `pctOfFlood(discharge, gauge)` — normalises discharge against `normalMin`/`floodThreshold` per gauge config
- `classifyRisk(discharge, gauge)` — ≥70% → high, ≥35% → mid, else low
- `flyToGauge(i)` — pans map via `map.flyTo()`
- `togglePill(el, layer)` — toggles `layerState` and calls `map.setLayoutProperty()` to show/hide MapLibre layers
- Layer visibility state lives in `layerState = { radar, rivers, zones, gauges }`
- `switchState(state, btn)` — filters sidebar gauge list by AU state (QLD/NSW/VIC/WA/SA/NT)
- `initRadarFrames(api)` / `showFrame(pos)` / `animateRadar()` — manage RainViewer radar frame playback
- `checkAddressCoords(lat, lon, label)` — fetches flood + rain data for any coordinate, returns risk verdict
