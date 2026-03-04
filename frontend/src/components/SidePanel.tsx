import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip } from 'chart.js'
import { Gauge } from '../types'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip)

export function SidePanel({gauge, timeseries}: {gauge?: Gauge, timeseries: {t: string; value: number}[]}) {
  if (!gauge) return <aside className="sidepanel empty">Select a gauge</aside>
  const utc = gauge.observed_at ? new Date(gauge.observed_at).toUTCString() : '-'
  const local = gauge.observed_at ? new Date(gauge.observed_at).toLocaleString() : '-'
  return <aside className="sidepanel">
    <h2>{gauge.name}</h2>
    <p>{gauge.river_name} · {gauge.state}</p>
    <div className={`badge ${gauge.severity || 'normal'}`}>{gauge.severity || 'normal'}</div>
    <p>Current: <strong>{gauge.value?.toFixed(2)} {gauge.units}</strong></p>
    <p>Trend: {gauge.trend} ({gauge.rate_per_hr?.toFixed(3)} /hr)</p>
    <p>Observed UTC: {utc}</p>
    <p>Observed local: {local}</p>
    <Line data={{
      labels: timeseries.map(v => new Date(v.t).toLocaleDateString()),
      datasets: [{data: timeseries.map(v => v.value), borderColor: '#2d6cdf', pointRadius: 0}]
    }} options={{responsive: true, plugins: {legend: {display: false}}}} />
  </aside>
}
