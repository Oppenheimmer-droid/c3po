'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, accessToken, initAuth } = useAuthStore()

  useEffect(() => {
    initAuth()
  }, [])

  useEffect(() => {
    if (!accessToken && pathname.startsWith('/dashboard')) {
      router.replace('/auth/login')
      return
    }

    if (user && pathname.startsWith('/auth')) {
      router.replace('/dashboard')
      return
    }
  }, [user, accessToken, pathname])

  return <>{children}</>
}
