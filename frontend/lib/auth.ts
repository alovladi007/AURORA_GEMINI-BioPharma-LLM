/**
 * Authentication token storage and helpers.
 *
 * Tokens are stored in localStorage. For higher-security deployments this can be
 * swapped for httpOnly cookies + a refresh endpoint without changing call sites.
 */

import type { User } from './types'

const ACCESS_TOKEN_KEY = 'pharma_access_token'
const USER_KEY = 'pharma_user'

const isBrowser = typeof window !== 'undefined'

export function getAuthToken(): string | null {
  if (!isBrowser) return null
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setAuthToken(token: string): void {
  if (!isBrowser) return
  window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAuthToken(): void {
  if (!isBrowser) return
  window.localStorage.removeItem(ACCESS_TOKEN_KEY)
}

export function getStoredUser(): User | null {
  if (!isBrowser) return null
  const raw = window.localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function setStoredUser(user: User): void {
  if (!isBrowser) return
  window.localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearStoredUser(): void {
  if (!isBrowser) return
  window.localStorage.removeItem(USER_KEY)
}

export function clearSession(): void {
  clearAuthToken()
  clearStoredUser()
}

export function isAuthenticated(): boolean {
  return getAuthToken() !== null
}

/**
 * Decode a JWT payload without verifying the signature (client-side display only).
 * Never trust this for authorization — the backend verifies the signature.
 */
export function decodeJwtPayload<T = Record<string, unknown>>(token: string): T | null {
  try {
    const payload = token.split('.')[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded) as T
  } catch {
    return null
  }
}

/** Returns true if the JWT is expired (or unparseable). */
export function isTokenExpired(token: string | null): boolean {
  if (!token) return true
  const payload = decodeJwtPayload<{ exp?: number }>(token)
  if (!payload?.exp) return true
  // exp is seconds since epoch
  return payload.exp * 1000 <= Date.now()
}
