'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

// Demo credentials
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
        // 1. Login to get tokens
        const loginResponse = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(DEMO_USER),
        })

        if (!loginResponse.ok) {
          throw new Error('Login failed')
        }

        const tokens = await loginResponse.json()
        
        // 2. Store tokens in localStorage
        localStorage.setItem('c3po_tokens', JSON.stringify({
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
          expires_at: Date.now() + 7 * 24 * 60 * 60 * 1000,
        }))

        // 3. Get user data
        const userResponse = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
          headers: { 'Authorization': `Bearer ${tokens.access_token}` },
        })

        if (!userResponse.ok) {
          throw new Error('Failed to get user')
        }

        const user = await userResponse.json()
        
        // 4. Store tenant ID
        if (user.tenant_id) {
          localStorage.setItem('c3po_tenant', user.tenant_id)
        }

        console.log('Auto-login successful:', user.email)
        toast.success('¡Bienvenido!')
        
        // 5. Redirect to dashboard
        router.push('/dashboard')
      } catch (error) {
        console.error('Auto-login failed:', error)
        toast.error('Error al iniciar sesión automáticamente')
        
        // If auto-login fails, go to regular login
        router.push('/auth/login')
      }
    }

    autoLogin()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-accent-50">
      <div className="text-center">
        <div className="animate-spin h-16 w-16 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-6" />
        <h2 className="text-xl font-semibold text-gray-700">Iniciando sesión...</h2>
        <p className="text-gray-500 mt-2">Accediendo automáticamente al dashboard</p>
      </div>
    </div>
  )
}