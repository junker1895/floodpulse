# FloodWatch — Project Reference

> This file is the single source of truth for the FloodWatch project.
> Claude should read this at the start of any new conversation before touching code.
> Update this file whenever significant decisions are made.

---

## Identity

| Field | Value |
|---|---|
| **App name** | FloodWatch |
| **Domain** | flood.watch (owned) |
| **Repo** | github.com/junker1895/floodpulse |
| **Live URL** | https://junker1895.github.io/floodpulse |
| **Builder** | Solo developer |
| **Status** | Australia prototype — functional but unpolished |

The repo is named `floodpulse` for historical reasons. The product is called **FloodWatch**. Do not rename the repo without being asked.

---

## Purpose

FloodWatch is a **map-first, real-time flood awareness platform** for the general public, emergency services, and government agencies worldwide.

Inspired by **Windy.com** — the benchmark is: simple, clean, easy to understand at a glance, visually compelling. If Windy shows wind elegantly, FloodWatch should show water the same way.

### What it does
- Shows animated river flow (eventually global)
- Live river discharge levels at gauge sites
- Animated radar rainfall overlay
- Address safety checker ("is my address at flood risk right now?")
- Flood risk verdict based on GPS location

### What makes it different from BOM / other tools
- **Visual / map-first** — BOM is text-heavy and hard to navigate under stress
- **Animated flow** — you can see rivers moving, not just read numbers
- **Address checker** — one input, instant verdict, designed for use during an actual flood event
- **Global** — not tied to any single country's warning system

---

## Data & Content Licensing Policy

All data sources, map imagery, icons, and embedded content must be **open source, Creative Commons licensed, or explicitly free for commercial use**. Do not integrate any data source, image, or third-party content without first confirming its license is compatible with a commercial product.

Current sources and their licenses:
| Source | License |
|---|---|
| OpenStreetMap | ODbL (open, attribution required) |
| GloFAS / Open-Meteo | CC BY 4.0 |
| RainViewer | Free tier — confirm commercial terms before scaling |
| BOM Geofabric | © Commonwealth of Australia (BOM) — attribution required, confirm commercial use terms |
| HydroRIVERS (future) | CC BY 4.0 |
| Nominatim / OSM geocoding | ODbL |

---

## What FloodWatch Must Never Do

- **Claim to replace official warnings** — always defer to local emergency services
- **Give legally accurate flood risk advice** — all verdicts are informational only
- **Require an account to access the free map** — core experience is always free, no login needed
- **Be Australia-only forever** — every architectural decision must be compatible with global expansion

---

## Business Model

**Freemium — public-first, with meaningful revenue from both individuals and organisations.**

The public use case drives scale and trust. Scale and trust are what make the council and government pitch work. A council is far more likely to pay for a tool their residents already use.

Advertising is acceptable if done tastefully and only where it doesn't undermine trust (e.g. never during an active flood event alert).

### Free tier — no account required
- Live map, radar, river flow animation
- Manual address safety check
- Current conditions at all public gauges
- The full core experience — this is what goes viral during flood events

### Free account (email signup)
- Save home address and watched locations
- Basic email alerts when a watched river crosses MODERATE threshold
- 30-day river history per location

### Pro — individual (~$5–10/month, meaningful revenue stream)
- Push notifications (mobile) in addition to email
- Multi-location watching (holiday house, parents' place, investment property)
- 7-day flood forecast per location
- Flood history reports — how many times has this area flooded in 5 years
- Early warning — alert X hours before predicted threshold crossing, not just when it happens
- Offline mode / PWA with cached data for when internet drops during a flood

### Council / Government — internal tool (~$50–200/month per organisation)
- Used internally by councils and emergency services for situational awareness and decision making
- Custom gauge network support (use their own sensors)
- Bulk location and catchment monitoring
- CSV/PDF flood reports for planning and insurance purposes
- API access for integration into existing emergency management platforms
- Custom alert thresholds
- SLA — guaranteed uptime during active flood events
- Dedicated support during events

### Enterprise / B2G (custom pricing)
- Full raw data feed
- White-label options
- Custom integrations
- Available globally — same model as Australia, targeting councils and emergency services worldwide

---

## Geographic Scope

- **Now:** Australia
- **Goal:** Every country — FloodWatch is a global product like Windy.com, not an Australian product
- Every architecture decision must be compatible with global expansion
- Council/government customers are a global target, not just Australian

---

## Risk Levels

Simple colour-coded system. **Not based on BOM or any single country's scale** — must work globally.

| Level | Colour | Meaning |
|---|---|---|
| LOW | Green | Rivers within normal range |
| MODERATE | Amber | Elevated — monitor closely |
| HIGH | Red | Flood conditions — take action |

Thresholds derived from GloFAS historical baselines per gauge. Approximate until real gauge data per country is integrated.

---

## Visual Design

- **Inspiration:** Windy.com — sparse, data-forward, no clutter, immediately understandable
- **Theme:** Dark by default. Light mode is a planned feature — implement when building settings
- **Typography:** Outfit (headings, body) + JetBrains Mono (all data/numbers)
- **Colour palette:** Deep navy backgrounds, cyan/blue accents, green/amber/red risk colours
- **No light mode yet** — to be added as a feature, not a current priority

---

## Current Tech Stack

### Frontend
- **Single `index.html`** — entire app lives here
- **Leaflet** — map rendering (to be replaced with MapLibre GL at global phase)
- **Canvas API** — river flow animation (lines + particles drawn from GeoJSON)
- **Vanilla JS** — no frameworks, no build tools, no bundlers
- **GitHub Pages** — free static hosting

### River flow system
- Three GeoJSON LOD files loaded into memory on demand:
  - `rivers-global.geojson` — zoom 2–5, stream order 1–3 (Amazon/Murray scale), ~3MB
  - `rivers-regional.geojson` — zoom 6–8, stream order 1–5, ~15MB
  - `rivers-local.geojson` — zoom 9+, stream order 1–7, ~40MB
- `lodForZoom(zoom)` selects correct LOD — global/regional/local
- Each LOD is fetched once and cached in memory — subsequent pans are instant local filtering
- Screen coordinates pre-cached in `screenPtsCache` — rebuilt on moveend, never per-frame
- HydroRIVERS geometry is already in correct flow direction — no reversal needed
- `width` pre-calculated from `ORD_FLOW` by processing script (order 1 = widest)
- Max 400 particles, prioritised by river width
- No `shadowBlur` — too expensive on canvas at scale
- River lines drawn on canvas from GeoJSON, particles animate on top

### Repo structure
```
floodpulse/
├── index.html                    # Entire frontend app
├── rivers-global.geojson         # HydroRIVERS zoom 2-5 (stream order 1-3)
├── rivers-regional.geojson       # HydroRIVERS zoom 6-8 (stream order 1-5)
├── rivers-local.geojson          # HydroRIVERS zoom 9+  (stream order 1-7)
├── process_hydrorivers.py        # One-time script to regenerate river GeoJSON files
└── PROJECT.md                    # This file
```

---

## Data Sources

| Source | Purpose | Status | Notes |
|---|---|---|---|
| GloFAS via Open-Meteo | River discharge forecasts at gauges | ✅ Live | Approximate — not real BOM gauges |
| Open-Meteo | Hourly rainfall forecasts | ✅ Live | |
| RainViewer | Animated radar tiles | ✅ Live | Rate limiting (429s) at high zoom |
| BOM Geofabric V3.3 | Australian river geometry | ❌ Replaced | Switched to HydroRIVERS for global consistency |
| Nominatim (OSM) | Address geocoding | ✅ Live | |
| HydroRIVERS (WWF/USGS) | Global river geometry, all LODs | ✅ Live | CC BY 4.0, processed via process_hydrorivers.py |

### HydroRIVERS — key facts
- Download: https://www.hydrosheds.org/products/hydrorivers (free account required)
- License: CC BY 4.0 — attribution required in app footer
- Key fields: `ORD_FLOW` (stream order 1–10), `UPLAND_SKM` (upstream area km²), `LENGTH_KM`
- Geometry is already in correct flow direction — no reversal logic needed
- Processed locally via `process_hydrorivers.py` → three static GeoJSON files committed to repo
- Files never need updating unless HydroRIVERS releases a new version

---

## Gauge Network (Current — 30 sites)

Data from GloFAS, not real BOM gauges. Thresholds manually estimated.

| State | Gauges |
|---|---|
| QLD | Colleges Crossing, Lowood, Kilcoy, Rosewood, Dayboro, Townsville, Cairns, Rockhampton, Roma |
| NSW | Windsor, Penrith, Grafton, Bourke, Wagga Wagga, Dubbo, Lismore |
| VIC | Melbourne, Shepparton, Wodonga, Traralgon, Ballarat |
| WA | Perth (Swan R.), Busselton, Broome, Port Hedland |
| SA | Adelaide, Renmark, Mt Gambier |
| NT | Darwin, Katherine |

---

## Known Issues

| Issue | Priority | Notes |
|---|---|---|
| Gauge data is GloFAS not real BOM | High | Requires backend proxy to fix |
| River particles visual quality | High | Density / zoom filtering still being tuned |
| RainViewer 429 rate limiting | Medium | Throttled with updateWhenIdle |
| No light mode | Low | Planned feature |
| No favicon | Low | 404 on favicon.ico |

---

## Planned Features (no fixed order — to be decided)

- Real BOM gauge data (replace GloFAS) — needs backend
- Share / screenshot button — key for virality during flood events
- Watch mode — "alert me if this river rises" on return visit
- SEO — meta tags, og:image, structured data for "[suburb] flooding" searches
- Light mode
- Mobile PWA — installable, offline cache
- Backend — Python + Docker proxy for BOM and international gauge APIs
- Accounts + payments (Stripe) for Pro tier
- Global expansion — HydroRIVERS + MapLibre GL rewrite

---

## Backend (Future)

**No backend yet** — everything is static GitHub Pages.

When a backend is needed:
- **Language:** Python
- **Containerised:** Docker
- **Database:** PostgreSQL
- **Primary use cases:** Proxy BOM + international gauge APIs (add CORS headers), cache responses, serve real gauge data, handle accounts and payments
- **Hosting:** TBD — VPS or Cloudflare Workers

---

## Global Expansion Plan (Future Phase)

When expanding beyond Australia:

1. **Replace BOM Geofabric with HydroRIVERS** (WWF/USGS)
   - Global, consistent attributes, free
   - `ORD_FLOW` stream order (1–10) maps directly to zoom levels
   - Has flow direction + upstream area — everything we need
   - ~400MB shapefile → ~80–120MB as PMTiles

2. **Replace Leaflet with MapLibre GL**
   - Native vector tile rendering (GPU accelerated)
   - Zoom-interpolated river styling via stream order
   - Proper flow animation via shaders (true Windy-style)

3. **Tile pipeline**
   ```
   HydroRIVERS.shp → ogr2ogr → tippecanoe → PMTiles → Cloudflare R2
   ```

4. **Backend** — Python + Docker, proxying international gauge APIs per country

---

## Claude's Rules for This Codebase

1. **Do not split `index.html` into multiple files** unless explicitly asked
2. **No build tools, npm, webpack, or bundlers** — vanilla JS only
3. **When replacing something, delete the old code** — don't leave dead code. But always check whether the code is used elsewhere before deleting. Never delete code that serves another function
4. **Don't make mistakes** — read the full relevant section before editing. Check your work. If unsure, read more code before acting
5. **Mobile is critical** — every change must work on a 375px screen. People use this during floods on their phones
6. **No paid APIs without asking first**
7. **No storing user data** — until accounts are explicitly built
8. **Performance matters** — no canvas shadowBlur, cache expensive calculations, nothing heavy per-frame
9. **When something isn't working, read the actual code** — don't guess

---

*Last updated: March 2026*
*Update this file when major decisions are made.*
