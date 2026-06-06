'use client'

/**
 * Authentication context — exposes the current user, auth status, and
 * login/register/logout actions to the whole app.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { authApi } from './api'
import {
  clearSession,
  getAuthToken,
  getStoredUser,
  isTokenExpired,
  setAuthToken,
  setStoredUser,
} from './auth'
import type { LoginCredentials, RegisterData, User } from './types'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<User>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // On mount, hydrate from storage and validate the token against the backend.
  useEffect(() => {
    let cancelled = false

    async function bootstrap() {
      const token = getAuthToken()
      if (!token || isTokenExpired(token)) {
        clearSession()
        if (!cancelled) {
          setUser(null)
          setIsLoading(false)
        }
        return
      }

      // Optimistically use cached user, then verify with /me.
      const cached = getStoredUser()
      if (cached && !cancelled) setUser(cached)

      try {
        const { data } = await authApi.me()
        if (!cancelled) {
          setUser(data)
          setStoredUser(data)
        }
      } catch {
        if (!cancelled) {
          clearSession()
          setUser(null)
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    bootstrap()
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (credentials: LoginCredentials) => {
    const { data } = await authApi.login(credentials)
    setAuthToken(data.access_token)
    const me = await authApi.me()
    setUser(me.data)
    setStoredUser(me.data)
  }, [])

  const register = useCallback(async (payload: RegisterData) => {
    const { data } = await authApi.register(payload)
    return data
  }, [])

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } catch {
      // Logout is best-effort; clear local session regardless.
    } finally {
      clearSession()
      setUser(null)
    }
  }, [])

  const refreshUser = useCallback(async () => {
    try {
      const { data } = await authApi.me()
      setUser(data)
      setStoredUser(data)
    } catch {
      clearSession()
      setUser(null)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (ctx === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
