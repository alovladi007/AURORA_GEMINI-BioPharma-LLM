'use client'

/**
 * Top navigation bar with auth-aware user menu.
 */

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useAuth } from '@/lib/auth-context'

const NAV_LINKS = [
  { href: '/projects', label: 'Projects' },
  { href: '/drug-design', label: 'Drug Design' },
  { href: '/clinical-trials', label: 'Clinical Trials' },
  { href: '/repurposing', label: 'Repurposing' },
  { href: '/safety', label: 'Safety' },
]

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth()
  const router = useRouter()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-lg font-bold text-blue-700">
            AURORA<span className="text-gray-400"> · </span>
            <span className="text-gray-700">BioPharma</span>
          </Link>
          {isAuthenticated && (
            <div className="hidden gap-4 md:flex">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-sm text-gray-600 transition hover:text-blue-700"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="relative">
          {isAuthenticated ? (
            <>
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-xs font-semibold text-white">
                  {(user?.full_name || user?.username || '?').charAt(0).toUpperCase()}
                </span>
                <span className="hidden sm:inline">{user?.username}</span>
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-md border border-gray-200 bg-white py-1 shadow-lg">
                  <div className="border-b border-gray-100 px-4 py-2">
                    <p className="text-sm font-medium text-gray-900">{user?.full_name || user?.username}</p>
                    <p className="truncate text-xs text-gray-500">{user?.email}</p>
                    <p className="mt-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium uppercase text-blue-700">
                      {user?.role}
                    </p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Link href="/login" className="text-sm text-gray-600 hover:text-blue-700">
                Log in
              </Link>
              <Link
                href="/register"
                className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                Sign up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
