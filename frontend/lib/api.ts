/**
 * API client for Pharma AI Platform backend
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios'
import { getAuthToken, clearSession } from './auth'
import type {
  AuthToken,
  User,
  LoginCredentials,
  RegisterData,
  MoleculeView,
  JobLaunchResponse,
} from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1_PREFIX = '/api/v1'

/** Where to send the user when their session becomes invalid. */
const LOGIN_PATH = '/login'

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

  // Request interceptor: inject the JWT access token when present.
  client.interceptors.request.use(
    (config) => {
      const token = getAuthToken()
      if (token) {
        config.headers = config.headers ?? {}
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error)
  )

  // Response interceptor: centralized error handling + auth expiry redirect.
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      if (error.response) {
        const status = error.response.status
        console.error('API Error:', status, error.response.data)

        // On 401 (expired/invalid token) clear the session and bounce to login,
        // unless the failing request was itself an auth call.
        const url = error.config?.url ?? ''
        const isAuthCall = url.includes('/auth/login') || url.includes('/auth/register')
        if (status === 401 && !isAuthCall && typeof window !== 'undefined') {
          clearSession()
          if (window.location.pathname !== LOGIN_PATH) {
            const next = encodeURIComponent(window.location.pathname)
            window.location.assign(`${LOGIN_PATH}?next=${next}`)
          }
        }
      } else if (error.request) {
        console.error('Network Error:', error.message)
      } else {
        console.error('Error:', error.message)
      }
      return Promise.reject(error)
    }
  )

  return client
}

export const apiClient = createApiClient()

/**
 * Authentication API.
 * Matches backend `/api/v1/auth/*` endpoints.
 */
export const authApi = {
  register: (data: RegisterData) =>
    apiClient.post<User>('/auth/register', data),
  login: (credentials: LoginCredentials) =>
    apiClient.post<AuthToken>('/auth/login', credentials),
  me: () => apiClient.get<User>('/auth/me'),
  refresh: () => apiClient.post<AuthToken>('/auth/refresh'),
  logout: () => apiClient.post<{ message: string }>('/auth/logout'),
  changePassword: (data: { old_password: string; new_password: string }) =>
    apiClient.post<{ message: string }>('/auth/change-password', data),
}

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

// Clinical Trials
export const clinicalTrialsApi = {
  recruitPatients: (data: any) => apiClient.post('/clinical-trials/recruit', data),
  designTrial: (data: any) => apiClient.post('/clinical-trials/design', data),
  generateSafetyPlan: (data: any) => apiClient.post('/clinical-trials/safety-monitoring', data),
}

// Drug Repurposing
export const repurposingApi = {
  mineKnowledgeGraph: (data: any) => apiClient.post('/repurposing/knowledge-graph', data),
  predictMechanism: (data: any) => apiClient.post('/repurposing/mechanism', data),
  discoverCombinations: (data: any) => apiClient.post('/repurposing/combinations', data),
}

// Safety
export const safetyApi = {
  predictADMET: (data: any) => apiClient.post('/safety/admet', data),
  predictToxicity: (data: any) => apiClient.post('/safety/toxicity', data),
  screenDDI: (data: any) => apiClient.post('/safety/ddi', data),
}

// Molecule visualization
export const visualizationApi = {
  molecule: (smiles: string, width = 350, height = 300) =>
    apiClient.get<MoleculeView>('/visualize/molecule', {
      params: { smiles, width, height },
    }),
  molecules: (smiles_list: string[], width = 250, height = 200) =>
    apiClient.post<MoleculeView[]>('/visualize/molecules', { smiles_list, width, height }),
}

// Training orchestration
export const trainingApi = {
  launchSAR: (data: {
    project_id: number
    target?: string
    input_csv?: string
    model_name?: string
    max_records?: number
    n_estimators?: number
    max_depth?: number
  }) => apiClient.post<JobLaunchResponse>('/training/sar', data),
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
