import { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Popup, useMap } from 'react-leaflet'
import { Gauge } from './types'
import { TopBar } from './components/TopBar'
import { Legend } from './components/Legend'
import { SidePanel } from './components/SidePanel'
import { HelpModal } from './components/HelpModal'

const API = 'http://localhost:8000/api'

function FlyTo({gauge}:{gauge?: Gauge}) {
  const map = useMap()
  useEffect(() => { if (gauge) map.flyTo([gauge.lat, gauge.lon], 10) }, [gauge, map])
  return null
}

export default function App() {
  const [gauges, setGauges] = useState<Gauge[]>([])
  const [rivers, setRivers] = useState<any>(null)
  const [selected, setSelected] = useState<Gauge>()
  const [series, setSeries] = useState<{t:string;value:number}[]>([])
  const [query, setQuery] = useState('')
  const [showGauges, setShowGauges] = useState(true)
  const [showRivers, setShowRivers] = useState(true)
  const [risingOnly, setRisingOnly] = useState(false)
  const [helpOpen, setHelpOpen] = useState(false)

  useEffect(() => { fetch(`${API}/rivers`).then(r => r.json()).then(setRivers) }, [])
  useEffect(() => {
    const u = new URL(`${API}/gauges`)
    if (query) u.searchParams.set('q', query)
    if (risingOnly) u.searchParams.set('rising_fast_only', 'true')
    fetch(u).then(r => r.json()).then(setGauges)
  }, [query, risingOnly])

  useEffect(() => {
    if (!selected) return
    fetch(`${API}/gauges/${selected.gauge_id}/timeseries?hours=168`).then(r => r.json()).then(setSeries)
  }, [selected])

  const markerColor = (sev?: string) => sev === 'rising_fast' ? '#ff5f5f' : sev === 'falling_fast' ? '#7e8cff' : '#3ecf8e'
  const visibleGauges = useMemo(() => gauges, [gauges])

  return <div className="app">
    <TopBar {...{query,setQuery,showGauges,setShowGauges,showRivers,setShowRivers,risingOnly,setRisingOnly}} onHelp={() => setHelpOpen(true)} />
    <div className="content">
      <MapContainer center={[-27.5, 152.9]} zoom={7} className="map">
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OSM" />
        {showRivers && rivers && <GeoJSON data={rivers} style={{color:'#3c79ff', weight:3, dashArray:'8 6', opacity:0.7}}/>}
        {showGauges && visibleGauges.map(g => (
          <CircleMarker key={g.gauge_id} center={[g.lat,g.lon]} radius={8} pathOptions={{color: markerColor(g.severity)}}
            className={g.severity === 'rising_fast' ? 'pulse' : ''} eventHandlers={{click: () => setSelected(g)}}>
            <Popup>{g.name} {g.value}{g.units}</Popup>
          </CircleMarker>
        ))}
        <FlyTo gauge={selected} />
      </MapContainer>
      <Legend />
      <SidePanel gauge={selected} timeseries={series} />
      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  </div>
}
