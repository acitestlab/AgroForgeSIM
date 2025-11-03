import axios, { AxiosError, AxiosInstance } from 'axios'

/** =========================
 * Types
 * ========================== */
export type CropMap = Record<string, string[]>

export interface CropsResponse {
  supported_crop_categories?: CropMap
  categories?: CropMap
  total_crops?: number
}

export interface CurrentWeather {
  temp_c: number
  humidity: number
  windspeed: number
  provider: string
  ts?: string
}

export interface ForecastDay {
  date: string
  tmin: number | null
  tmax: number | null
  rain: number
  rad: number
  et0: number
}

export interface ScenarioRequest {
  crop: string
  area_acres: number
  lat: number
  lon: number
  horizon_hours?: number
  irrigation?: boolean
  soil_quality?: 'low' | 'medium' | 'high'
}

export interface YieldBreakdown {
  expected_yield_tonnes: number
  water_usage_m3: number
  cycle_days: number
  notes?: string | null
}

export interface SimulationResult {
  crop: string
  area_acres: number
  yield_estimate: YieldBreakdown
  weather_summary: Record<string, unknown>
}

export interface SurveyFeature {
  id: string
  name: string
  geometry: Record<string, unknown>
  properties?: Record<string, unknown>
}

export interface SurveyImportRequest {
  name: string
  type: 'geojson' | 'kml' | 'dxf'
  features: SurveyFeature[]
}

export interface HarvestPlanResponse {
  status?: string
  plan?: unknown
  [k: string]: unknown
}

/** =========================
 * Axios instance
 * ========================== */
const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 20000,
  headers: {
    'X-Requested-With': 'XMLHttpRequest',
  },
})

// Response interceptor: always return data, rethrow typed errors
api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    // Optionally map known backend error shapes here
    return Promise.reject(err)
  }
)

/** =========================
 * Helpers
 * ========================== */
function normalizeCrops(resp: CropsResponse): CropMap {
  // Backend might return either {supported_crop_categories} or {categories}
  return resp.supported_crop_categories ?? resp.categories ?? {}
}

/** =========================
 * API functions
 * ========================== */

// Health (useful for readiness checks in the UI if needed)
export async function getHealth(signal?: AbortSignal): Promise<{ status: string }> {
  const { data } = await api.get('/health', { signal })
  return data
}

// Crops
export async function getCrops(signal?: AbortSignal): Promise<CropMap> {
  const { data } = await api.get<CropsResponse>('/crops', { signal })
  return normalizeCrops(data)
}

// Weather
export async function getCurrentWeather(
  lat: number,
  lon: number,
  signal?: AbortSignal
): Promise<CurrentWeather> {
  const { data } = await api.get<CurrentWeather>('/weather/current', {
    params: { lat, lon },
    signal,
  })
  return data
}

export async function getForecast(
  lat: number,
  lon: number,
  hours = 48,
  signal?: AbortSignal
): Promise<ForecastDay[]> {
  const { data } = await api.get<ForecastDay[]>('/weather/forecast', {
    params: { lat, lon, hours },
    signal,
  })
  return data
}

// Simulation
export async function simulate(payload: ScenarioRequest, signal?: AbortSignal): Promise<SimulationResult> {
  const { data } = await api.post<SimulationResult>('/simulate', payload, { signal })
  return data
}

// Harvest plan
export async function harvestPlan(payload: ScenarioRequest, signal?: AbortSignal): Promise<HarvestPlanResponse> {
  const { data } = await api.post<HarvestPlanResponse>('/harvest/plan', payload, { signal })
  return data
}

// Survey import (echo/placeholder per backend)
export async function importSurvey(payload: SurveyImportRequest, signal?: AbortSignal): Promise<Record<string, unknown>> {
  const { data } = await api.post<Record<string, unknown>>('/survey/import', payload, { signal })
  return data
}

export default api
