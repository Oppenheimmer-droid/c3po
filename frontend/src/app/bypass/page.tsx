'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

// Demo credentials - updated
const DEMO_USER = {
  email: 'test@demo.com',
  password: 'Test1234',
}

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://c3po-production-0c24.up.railway.app'

export default function BypassPage() {
  const router = useRouter()

  useEffect(() => {
    const autoLogin = async () => {
      try {
        const loginResponse = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(DEMO_USER),
        })

        if (!loginResponse.ok) throw new Error('Login failed')

        const tokens = await loginResponse.json()
        localStorage.setItem('c3po_tokens', JSON.stringify({
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
          expires_at: Date.now() + 7 * 24 * 60 * 60 * 1000,
        }))

        const userResponse = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
          headers: { 'Authorization': `Bearer ${tokens.access_token}` },
        })

        if (!userResponse.ok) throw new Error('Failed to get user')

        const user = await userResponse.json()
        if (user.tenant_id) localStorage.setItem('c3po_tenant', user.tenant_id)

        toast.success('¡Bienvenido!')
        router.push('/dashboard')
      } catch (error) {
        console.error('Auto-login failed:', error)
        toast.error('Error al iniciar sesión')
        router.push('/auth/login')
      }
    }

    autoLogin()
  }, [router])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
      <div className="animate-spin h-16 w-16 border-4 border-primary-500 border-t-transparent rounded-full mb-6" />
      <h2 className="text-2xl font-bold text-gray-800">Iniciando sesión automáticamente</h2>
      <p className="text-gray-500 mt-2">Accediendo al dashboard...</p>
      <div className="mt-6 flex items-center gap-2 text-sm text-gray-400">
        <svg className="animate-pulse w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/>
        </svg>
        <span> Cargando...</span>
      </div>
    </div>
  )
}
