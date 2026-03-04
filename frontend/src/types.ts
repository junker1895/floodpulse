export type Gauge = {
  gauge_id: string
  name: string
  state: string
  river_name?: string
  provider: string
  external_id: string
  lat: number
  lon: number
  observed_at?: string
  value?: number
  units?: string
  trend?: 'up' | 'down' | 'steady'
  rate_per_hr?: number
  severity?: 'rising_fast' | 'falling_fast' | 'normal'
  source?: string
}
