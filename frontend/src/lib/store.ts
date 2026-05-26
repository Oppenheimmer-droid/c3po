import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, UserSettings } from '@/types'
import { setTokens, clearTokens, setTenantId } from '@/lib/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  settings: UserSettings
  
  // Actions
  setUser: (user: User | null) => void
  login: (user: User, tokens: { access_token: string; refresh_token: string }) => void
  logout: () => void
  updateSettings: (settings: Partial<UserSettings>) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,
      settings: {
        theme: 'system',
        ai_provider: 'openai',
        notifications_enabled: true,
      },

      setUser: (user) => set({ 
        user, 
        isAuthenticated: !!user 
      }),

      login: (user, tokens) => {
        setTokens(tokens)
        setTenantId(user.tenant_id)
        set({ 
          user, 
          isAuthenticated: true,
          isLoading: false,
        })
      },

      logout: () => {
        clearTokens()
        set({ 
          user: null, 
          isAuthenticated: false,
          isLoading: false,
        })
      },

      updateSettings: (newSettings) => set((state) => ({
        settings: { ...state.settings, ...newSettings }
      })),

      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        settings: state.settings,
      }),
    }
  )
)

// Theme store
interface ThemeState {
  theme: 'light' | 'dark' | 'system'
  resolvedTheme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: 'system',
  resolvedTheme: 'light',

  setTheme: (theme) => {
    set({ theme })
    
    // Apply to document
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    
    if (theme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.classList.add(isDark ? 'dark' : 'light')
      set({ resolvedTheme: isDark ? 'dark' : 'light' })
    } else {
      root.classList.add(theme)
      set({ resolvedTheme: theme })
    }
  },
}))

// Chat UI store
interface ChatState {
  sessions: Array<{ id: string; title: string }>
  currentSessionId: string | null
  isStreaming: boolean
  
  setSessions: (sessions: Array<{ id: string; title: string }>) => void
  setCurrentSession: (sessionId: string | null) => void
  addSession: (session: { id: string; title: string }) => void
  removeSession: (sessionId: string) => void
  setStreaming: (streaming: boolean) => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessions: [],
  currentSessionId: null,
  isStreaming: false,

  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (sessionId) => set({ currentSessionId: sessionId }),
  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions]
  })),
  removeSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.id !== sessionId),
    currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
  })),
  setStreaming: (streaming) => set({ isStreaming: streaming }),
}))