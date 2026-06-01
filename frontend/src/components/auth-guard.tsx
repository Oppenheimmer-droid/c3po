'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const router = useRouter()
  const { isAuthenticated, isLoading, initAuth, setLoading } = useAuthStore()

  useEffect(() => {
    // Initialize auth on mount - reads tokens from localStorage and validates with backend
    if (isLoading) {
      initAuth().then((user) => {
        if (!user && requireAuth) {
          router.push('/auth/login')
        }
      })
    }
  }, []) // Only run on mount

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Verificando sesión...</p>
        </div>
      </div>
    )
  }

  // If auth is required and not authenticated, return null (will redirect)
  if (requireAuth && !isAuthenticated) {
    return null
  }

  // If auth is not required or user is authenticated, show children
  return <>{children}</>
}

// Simple component for pages that should redirect if authenticated (login/register)
export function GuestGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, initAuth } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (isLoading) {
      initAuth().then((user) => {
        if (user) {
          router.push('/dashboard')
        }
      })
    }
  }, []) // Only run on mount

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  // If already authenticated, return null (will redirect)
  if (isAuthenticated) {
    return null
  }

  return <>{children}</>
}