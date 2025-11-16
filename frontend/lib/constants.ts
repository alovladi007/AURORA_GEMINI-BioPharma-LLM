/**
 * Application constants
 */

export const APP_NAME = 'Pharma AI Platform'
export const APP_VERSION = '0.1.0'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const API_V1_PREFIX = '/api/v1'

/**
 * Module status
 */
export const MODULE_STATUS = {
  ENABLED: 'enabled',
  DISABLED: 'disabled',
  COMING_SOON: 'coming_soon',
} as const

/**
 * Project status
 */
export const PROJECT_STATUS = {
  ACTIVE: 'active',
  ARCHIVED: 'archived',
  COMPLETED: 'completed',
} as const

/**
 * Model status
 */
export const MODEL_STATUS = {
  TRAINING: 'training',
  READY: 'ready',
  FAILED: 'failed',
  DEPRECATED: 'deprecated',
} as const

/**
 * Toxicity thresholds
 */
export const TOXICITY_THRESHOLDS = {
  LOW: 0.3,
  MODERATE: 0.7,
  HIGH: 1.0,
} as const

/**
 * ADMET properties
 */
export const ADMET_PROPERTIES = [
  'absorption',
  'distribution',
  'metabolism',
  'excretion',
  'toxicity',
] as const

/**
 * Pagination defaults
 */
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
