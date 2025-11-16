import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format date to readable string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(d)
}

/**
 * Format number with commas
 */
export function formatNumber(num: number): string {
  return new Intl.NumberFormat('en-US').format(num)
}

/**
 * Truncate string to specified length
 */
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

/**
 * Sleep/delay utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Validate SMILES string (basic validation)
 */
export function isValidSMILES(smiles: string): boolean {
  // Basic validation - check for common SMILES characters
  const validChars = /^[A-Za-z0-9@+\-\[\]()=#$:\/\\%.]+$/
  return validChars.test(smiles) && smiles.length > 0
}

/**
 * Generate random ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 15)
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * Get color for toxicity/safety score
 */
export function getToxicityColor(score: number): string {
  if (score < 0.3) return 'text-green-600'
  if (score < 0.7) return 'text-yellow-600'
  return 'text-red-600'
}

/**
 * Get badge color for status
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'badge-success',
    pending: 'badge-warning',
    completed: 'badge-primary',
    failed: 'badge-danger',
  }
  return colors[status.toLowerCase()] || 'badge'
}
