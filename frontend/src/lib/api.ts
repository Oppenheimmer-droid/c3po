'use client'

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app/api'

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

const TOKEN_KEY = 'c3po_tokens'
const TENANT_KEY = 'c3po_tenant'
const TENANT_SLUG_KEY = 'c3po_tenant_slug'

interface TokenData {
  access_token: string
  refresh_token: string
  expires_at?: number
}

export const getTokens = (): TokenData | null => {
  if (typeof window === 'undefined') return null
  try {
    const stored = localStorage.getItem(TOKEN_KEY)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

export const setTokens = (tokens: { access_token: string; refresh_token: string }) => {
  if (typeof window === 'undefined') return
  localStorage.setItem(TOKEN_KEY, JSON.stringify({
    ...tokens,
    expires_at: Date.now() + 7 * 24 * 60 * 60 * 1000,
  }))
}

export const clearTokens = () => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(TENANT_KEY)
  localStorage.removeItem(TENANT_SLUG_KEY)
}

export const getAccessToken = (): string | null => getTokens()?.access_token ?? null
export const getRefreshToken = (): string | null => getTokens()?.refresh_token ?? null
export const getTenantId = (): string | null => typeof window !== 'undefined' ? localStorage.getItem(TENANT_KEY) : null
export const setTenantId = (id: string) => typeof window !== 'undefined' && localStorage.setItem(TENANT_KEY, id)
export const getTenantSlug = (): string | null => typeof window !== 'undefined' ? localStorage.getItem(TENANT_SLUG_KEY) : null
export const setTenantSlug = (slug: string) => typeof window !== 'undefined' && localStorage.setItem(TENANT_SLUG_KEY, slug)

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  const tenantId = getTenantId()
  if (tenantId) config.headers['X-Tenant-ID'] = tenantId
  const tenantSlug = getTenantSlug()
  if (tenantSlug) config.headers['X-Tenant-Slug'] = tenantSlug
  return config
}, (error) => Promise.reject(error))

let isRefreshing = false
let failedQueue: Array<{resolve: (v: unknown) => void; reject: (e?: unknown) => void}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(prom => error ? prom.reject(error) : prom.resolve(token))
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {_retry?: boolean}
    const url = originalRequest?.url || ''
    if (url.includes('/auth/')) return Promise.reject(error)
    
    if (error.response?.status === 401 && !originalRequest?._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => failedQueue.push({ resolve, reject }))
          .then(token => { originalRequest!.headers.Authorization = `Bearer ${token}`; return api(originalRequest!) })
          .catch(err => Promise.reject(err))
      }
      originalRequest!._retry = true
      isRefreshing = true
      const refreshToken = getRefreshToken()
      if (!refreshToken) { isRefreshing = false; return Promise.reject(error) }
      
      try {
        const response = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken })
        const { access_token, refresh_token: newRefreshToken } = response.data
        setTokens({ access_token, refresh_token: newRefreshToken })
        processQueue(null, access_token)
        originalRequest!.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest!)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        clearTokens()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
