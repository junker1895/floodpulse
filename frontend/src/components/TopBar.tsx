type Props = {
  query: string
  setQuery: (v: string) => void
  showGauges: boolean
  setShowGauges: (v: boolean) => void
  showRivers: boolean
  setShowRivers: (v: boolean) => void
  risingOnly: boolean
  setRisingOnly: (v: boolean) => void
  onHelp: () => void
}

export function TopBar(p: Props) {
  return <div className="topbar">
    <input placeholder="Search town or gauge" value={p.query} onChange={e => p.setQuery(e.target.value)} />
    <label><input type="checkbox" checked={p.showGauges} onChange={e => p.setShowGauges(e.target.checked)} /> Gauges</label>
    <label><input type="checkbox" checked={p.showRivers} onChange={e => p.setShowRivers(e.target.checked)} /> Rivers</label>
    <label><input type="checkbox" checked={p.risingOnly} onChange={e => p.setRisingOnly(e.target.checked)} /> Rising fast</label>
    <button onClick={p.onHelp}>What does this mean?</button>
  </div>
}
