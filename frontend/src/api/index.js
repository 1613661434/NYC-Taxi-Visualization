import axios from 'axios'

const api = axios.create({ baseURL: 'http://127.0.0.1:8000' })

export function fetchDashboard(params) {
  return api.get('/api/dashboard-data', { params }).then(r => r.data)
}

export function fetchMissingValues(params) {
  return api.get('/api/missing-values', { params }).then(r => r.data)
}

export function fetchClustering(params) {
  return api.get('/api/clustering', { params }).then(r => r.data)
}

export function fetchPredictionTrain(params) {
  return api.get('/api/prediction/train', { params }).then(r => r.data)
}

export function fetchPredictionCompare(params) {
  return api.get('/api/prediction/compare', { params }).then(r => r.data)
}

export function fetchMonthlyPrediction(params) {
  return api.get('/api/prediction/monthly', { params }).then(r => r.data)
}

export function fetchPreference(params) {
  return api.get('/api/preference', { params }).then(r => r.data)
}

export function fetchCorrelationAdvanced(params) {
  return api.get('/api/correlation-advanced', { params }).then(r => r.data)
}

export function fetchMapData(params) {
  return api.get('/api/map-data', { params }).then(r => r.data)
}

export function fetchTimelineData(params) {
  return api.get('/api/timeline-data', { params }).then(r => r.data)
}

export function fetchDrillDown(params) {
  return api.get('/api/drill-down', { params }).then(r => r.data)
}

export function fetchCrossCorrelation(params) {
  return api.get('/api/cross-correlation', { params }).then(r => r.data)
}

export function fetchBoroughAnalysis(params) {
  return api.get('/api/borough-analysis', { params }).then(r => r.data)
}
