import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { BACKEND_URL } from '@/lib/config'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  login: (user: User, tokens: { access_token: string; refresh_token: string }) => void
  logout: () => void
  initAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,

      login: (user, tokens) => {
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token
        })
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null
        })
      },

      initAuth: async () => {
        const { accessToken } = get()
        if (!accessToken) return

        try {
          const res = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
            headers: { Authorization: `Bearer ${accessToken}` }
          })

          if (!res.ok) {
            get().logout()
            return
          }

          const user = await res.json()
          set({ user })
        } catch {
          get().logout()
        }
      }
    }),
    {
      name: 'auth-storage'
    }
  )
)
