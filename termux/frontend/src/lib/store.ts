import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { BACKEND_URL } from '@/lib/config'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
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
      isAuthenticated: false,
      isLoading: true,

      login: (user, tokens) => {
        set({
          user,
          accessToken: tokens.access_token,
          refreshToken: tokens.refresh_token,
          isAuthenticated: true,
          isLoading: false
        })
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false
        })
      },

      initAuth: async () => {
        set({ isLoading: true })
        const { accessToken } = get()
        if (!accessToken) {
          set({ isLoading: false })
          return
        }

        try {
          const res = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
            headers: { Authorization: `Bearer ${accessToken}` }
          })

          if (!res.ok) {
            get().logout()
            return
          }

          const user = await res.json()
          set({ user, isAuthenticated: true, isLoading: false })
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

// Chat Store
interface Session {
  id: string
  title: string
}

interface ChatState {
  sessions: Session[]
  currentSessionId: string | null
  streaming: boolean
  setSessions: (sessions: Session[]) => void
  setCurrentSession: (id: string) => void
  addSession: (session: Session) => void
  setStreaming: (streaming: boolean) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>()((set) => ({
  sessions: [],
  currentSessionId: null,
  streaming: false,
  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (id) => set({ currentSessionId: id }),
  addSession: (session) => set((state) => ({ sessions: [...state.sessions, session] })),
  setStreaming: (streaming) => set({ streaming }),
  clearChat: () => set({ currentSessionId: null, sessions: [] }),
}))
