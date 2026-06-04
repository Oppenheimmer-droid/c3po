import { create } from 'zustand'
import type { User, UserSettings } from '@/types'

// Demo credentials for auto-login (matches the credentials shown in the login UI)
const DEMO_USER = { email: 'admin@demo.com', password: 'admin123' }
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://c3po-production-0c24.up.railway.app'

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
  initAuth: () => Promise<User | null>
  autoLogin: () => Promise<boolean>
}

// Get tenant slug from localStorage
function getTenantSlug(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('c3po_tenant_slug')
}

// Save tenant slug to localStorage
function saveTenantSlug(slug: string) {
  localStorage.setItem('c3po_tenant_slug', slug)
}

// Get tokens from localStorage
function getTokens(): { access_token: string; refresh_token: string } | null {
  if (typeof window === 'undefined') return null
  const stored = localStorage.getItem('c3po_tokens')
  if (!stored) return null
  try {
    return JSON.parse(stored)
  } catch {
    return null
  }
}

// Save tokens to localStorage
function saveTokens(tokens: { access_token: string; refresh_token: string }) {
  localStorage.setItem('c3po_tokens', JSON.stringify({
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    expires_at: Date.now() + 7 * 24 * 60 * 60 * 1000,
  }))
}

// Clear tokens
function clearTokens() {
  localStorage.removeItem('c3po_tokens')
  localStorage.removeItem('c3po_tenant')
  localStorage.removeItem('c3po_tenant_slug')
}

// Auth store - NO PERSIST. Tokens in localStorage, user state in memory
export const useAuthStore = create<AuthState>()((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  settings: {
    theme: 'system',
    ai_provider: 'openai',
    notifications_enabled: true,
  },

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  login: (user, tokens) => {
    saveTokens(tokens)
    if (user.tenant_id) {
      localStorage.setItem('c3po_tenant', user.tenant_id)
    }
    // Extract tenant slug from user object or generate from tenant_name
    const tenantSlug = (user as any).tenant_slug || (user as any).tenant_name?.toLowerCase().replace(/\s+/g, '-') || 'default'
    saveTenantSlug(tenantSlug)
    set({ user, isAuthenticated: true, isLoading: false })
  },

  logout: () => {
    clearTokens()
    set({ user: null, isAuthenticated: false, isLoading: false })
  },

  updateSettings: (newSettings) => set((state) => ({
    settings: { ...state.settings, ...newSettings }
  })),

  setLoading: (loading) => set({ isLoading: loading }),

  // Auto-login with demo credentials
  autoLogin: async () => {
    try {
      const loginRes = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tenant-Slug': 'default',
        },
        body: JSON.stringify(DEMO_USER),
      })

      if (!loginRes.ok) throw new Error('Login failed')

      const tokens = await loginRes.json()
      saveTokens(tokens)

      const userRes = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
        headers: { 'Authorization': `Bearer ${tokens.access_token}` },
      })

      if (!userRes.ok) throw new Error('Failed to get user')

      const user = await userRes.json()
      if (user.tenant_id) localStorage.setItem('c3po_tenant', user.tenant_id)

      set({ user, isAuthenticated: true, isLoading: false })
      return true
    } catch (e) {
      console.error('Auto-login failed:', e)
      clearTokens()
      set({ user: null, isAuthenticated: false, isLoading: false })
      return false
    }
  },

  // Initialize auth from localStorage tokens (no auto-login)
  initAuth: async () => {
    const tokens = getTokens()
    const tenantSlug = getTenantSlug()
    
    // Check if we have a valid token
    if (tokens?.access_token) {
      try {
        // Direct fetch instead of using service (avoids axios interceptor issues)
        const headers: Record<string, string> = {
          'Authorization': `Bearer ${tokens.access_token}`,
        }
        if (tenantSlug) {
          headers['X-Tenant-Slug'] = tenantSlug
        }
        
        const userRes = await fetch(`${BACKEND_URL}/api/v1/auth/me`, {
          headers,
        })
        
        if (userRes.ok) {
          const user = await userRes.json()
          set({ user, isAuthenticated: true, isLoading: false })
          return user
        }
        // Token invalid - clear
        clearTokens()
      } catch {
        clearTokens()
      }
    }

    // No valid tokens - user needs to login
    set({ user: null, isAuthenticated: false, isLoading: false })
    return null
  },
}))

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