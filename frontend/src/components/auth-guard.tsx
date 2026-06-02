'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const router = useRouter()
  const { isLoading, isAuthenticated, initAuth, autoLogin } = useAuthStore()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const init = async () => {
      // Try to init auth (uses existing token or auto-login)
      const user = await initAuth()
      
      if (!user && requireAuth) {
        // Auto-login failed and auth required - redirect to login
        router.push('/auth/login')
      } else if (user && !requireAuth) {
        // User authenticated but page doesn't require auth (login page)
        router.push('/dashboard')
      } else {
        setReady(true)
      }
    }
    
    if (isLoading) {
      init()
    }
  }, [isLoading, requireAuth, router])

  if (isLoading || !ready) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-500">Iniciando sesión...</p>
        </div>
      </div>
    )
  }

  if (requireAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
        <div className="text-center">
          <p className="text-gray-500">Redirigiendo...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

// Simple component for pages that should redirect if authenticated (login/register)
export function GuestGuard({ children }: { children: React.ReactNode }) {
  const { isLoading, isAuthenticated, initAuth } = useAuthStore()
  const router = useRouter()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const init = async () => {
      const user = await initAuth()
      if (user) {
        router.push('/dashboard')
      } else {
        setReady(true)
      }
    }
    
    if (isLoading) {
      init()
    }
  }, [isLoading, router])

  if (isLoading || !ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return <>{children}</>
}