# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FloodWatch is a single-file HTML/JS/CSS prototype — a flood monitoring dashboard for SE Queensland, Australia. There is no build system, package manager, backend, or real data source.

## Development

Open `floodwatch-v2.html` directly in a browser. No build step required.

## Architecture

Everything lives in `floodwatch-v2.html`:

- **CSS** (`:root` vars → component styles) — dark theme using CSS custom properties; `--low` (green), `--mid` (yellow), `--high` (red) are the risk color tokens used throughout
- **Map** — Leaflet.js with OSM tiles, CSS-filtered dark. Flood zones are `L.circle`, rivers are `L.polyline`, gauges are `L.marker` with custom `divIcon` HTML
- **Rain canvas** — `<canvas id="rainCanvas">` overlaid on the map, animated via `requestAnimationFrame` with 350 simulated drops
- **Sidebar** — static HTML for alerts and gauges; timeline bars built dynamically from `tlData` array; sparkline drawn on `<canvas id="spark">`
- **Simulated live data** — a `setInterval` updates the "mm/hr now" readout using `Math.sin(Date.now()/9000)` to fake fluctuation

All gauge/alert/river data is hardcoded. There are no API calls or real-time data feeds.

## Key Patterns

- Risk level (`high`/`mid`/`low`) drives CSS class names on markers, gauge rows, and fill colors
- `focusGauge(el, lat, lng, name)` — called from sidebar gauge `onclick`, pans map via `map.flyTo()`
- `togglePill(el, layer)` — toggles `layerState` object and shows/hides flood zone circles or rain canvas
- Layer visibility state lives in `layerState = { rain, zones, gauges, roads }`
