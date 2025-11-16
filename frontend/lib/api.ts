/**
 * API client for Pharma AI Platform backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

/**
 * Create axios instance with default configuration
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_URL}${API_V1_PREFIX}`,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor for adding auth token
  client.interceptors.request.use(
    (config) => {
      // TODO: Add authentication token when auth is implemented
      // const token = getAuthToken()
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`
      // }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response) {
        // Server responded with error status
        console.error('API Error:', error.response.status, error.response.data)
      } else if (error.request) {
        // Request made but no response
        console.error('Network Error:', error.message)
      } else {
        // Something else happened
        console.error('Error:', error.message)
      }
      return Promise.reject(error)
    }
  )

  return client
}

export const apiClient = createApiClient()

/**
 * API service functions
 */

// Health
export const healthApi = {
  check: () => apiClient.get('/health'),
  live: () => apiClient.get('/health/live'),
  ready: () => apiClient.get('/health/ready'),
  metrics: () => apiClient.get('/health/metrics'),
}

// Projects (to be implemented)
export const projectsApi = {
  list: () => apiClient.get('/projects'),
  get: (id: string) => apiClient.get(`/projects/${id}`),
  create: (data: any) => apiClient.post('/projects', data),
  update: (id: string, data: any) => apiClient.put(`/projects/${id}`, data),
  delete: (id: string) => apiClient.delete(`/projects/${id}`),
}

// Drug Design (to be implemented)
export const drugDesignApi = {
  generate: (data: any) => apiClient.post('/drug-design/generate', data),
  predictSAR: (data: any) => apiClient.post('/drug-design/predict-sar', data),
  optimize: (data: any) => apiClient.post('/drug-design/optimize', data),
}

// Clinical Trials (to be implemented)
export const clinicalTrialsApi = {
  recruitPatients: (data: any) => apiClient.post('/clinical-trials/recruit', data),
  designTrial: (data: any) => apiClient.post('/clinical-trials/design', data),
  monitorSafety: (trialId: string) => apiClient.get(`/clinical-trials/${trialId}/safety`),
}

// Repurposing (to be implemented)
export const repurposingApi = {
  findIndications: (drugId: string) => apiClient.get(`/repurposing/indications/${drugId}`),
  analyzeMechanism: (data: any) => apiClient.post('/repurposing/mechanism', data),
  findCombinations: (data: any) => apiClient.post('/repurposing/combinations', data),
}

// Safety
export const safetyApi = {
  predictADMET: (data: any) => apiClient.post('/safety/admet', data),
  predictToxicity: (data: any) => apiClient.post('/safety/toxicity', data),
  screenDDI: (data: any) => apiClient.post('/safety/ddi', data),
}

// Datasets
export const datasetApi = {
  list: (params?: { project_id?: number; dataset_type?: string; skip?: number; limit?: number }) =>
    apiClient.get('/datasets', { params }),
  summary: (params?: { project_id?: number }) =>
    apiClient.get('/datasets/summary', { params }),
  get: (id: number) => apiClient.get(`/datasets/${id}`),
  create: (data: any) => apiClient.post('/datasets', data),
  update: (id: number, data: any) => apiClient.put(`/datasets/${id}`, data),
  delete: (id: number) => apiClient.delete(`/datasets/${id}`),
}

// ML Models
export const modelApi = {
  list: (params?: { project_id?: number; model_type?: string; skip?: number; limit?: number }) =>
    apiClient.get('/models', { params }),
  summary: (params?: { project_id?: number }) =>
    apiClient.get('/models/summary', { params }),
  get: (id: number) => apiClient.get(`/models/${id}`),
  create: (data: any) => apiClient.post('/models', data),
  update: (id: number, data: any) => apiClient.put(`/models/${id}`, data),
  delete: (id: number) => apiClient.delete(`/models/${id}`),
}

// Experiments
export const experimentApi = {
  list: (params?: {
    project_id?: number;
    model_id?: number;
    dataset_id?: number;
    status?: string;
    skip?: number;
    limit?: number
  }) => apiClient.get('/experiments', { params }),
  summary: (params?: { project_id?: number }) =>
    apiClient.get('/experiments/summary', { params }),
  get: (id: number) => apiClient.get(`/experiments/${id}`),
  create: (data: any) => apiClient.post('/experiments', data),
  update: (id: number, data: any) => apiClient.put(`/experiments/${id}`, data),
  delete: (id: number) => apiClient.delete(`/experiments/${id}`),
}

// Jobs
export const jobApi = {
  list: (params?: { project_id?: number; job_type?: string; status?: string; skip?: number; limit?: number }) =>
    apiClient.get('/jobs', { params }),
  summary: (params?: { project_id?: number }) =>
    apiClient.get('/jobs/summary', { params }),
  get: (id: number) => apiClient.get(`/jobs/${id}`),
  create: (data: any) => apiClient.post('/jobs', data),
  update: (id: number, data: any) => apiClient.put(`/jobs/${id}`, data),
  cancel: (id: number) => apiClient.post(`/jobs/${id}/cancel`),
  delete: (id: number) => apiClient.delete(`/jobs/${id}`),
}

/**
 * Error handling utilities
 */
export const getErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unknown error occurred'
}

/**
 * Type guards
 */
export const isApiError = (error: unknown): error is AxiosError => {
  return axios.isAxiosError(error)
}
