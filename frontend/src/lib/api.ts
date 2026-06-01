import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL || undefined,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management
export const getAccessToken = (): string | undefined => {
  if (typeof document !== 'undefined') {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'access_token') return value
    }
  }
  return undefined
}

export const getRefreshToken = (): string | undefined => {
  if (typeof document !== 'undefined') {
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=')
      if (name === 'refresh_token') return value
    }
  }
  return undefined
}

export const setTokens = (tokens: { access_token: string; refresh_token: string }) => {
  // Use direct document.cookie for better compatibility
  if (typeof document !== 'undefined') {
    document.cookie = `access_token=${tokens.access_token}; path=/; max-age=${7 * 24 * 60 * 60}; samesite=lax`
    document.cookie = `refresh_token=${tokens.refresh_token}; path=/; max-age=${7 * 24 * 60 * 60}; samesite=lax`
  }
  // Also use js-cookie as backup
  Cookies.set('access_token', tokens.access_token, { expires: 7, sameSite: 'lax' })
  Cookies.set('refresh_token', tokens.refresh_token, { expires: 7, sameSite: 'lax' })
}

export const clearTokens = () => {
  if (typeof document !== 'undefined') {
    document.cookie = 'access_token=; path=/; max-age=0'
    document.cookie = 'refresh_token=; path=/; max-age=0'
  }
  Cookies.remove('access_token')
  Cookies.remove('refresh_token')
}

// Tenant management
export const getTenantId = (): string | undefined => {
  return Cookies.get('tenant_id')
}

export const setTenantId = (tenantId: string) => {
  Cookies.set('tenant_id', tenantId, { expires: 7, secure: true, sameSite: 'strict' })
}

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken()
    const tenantId = getTenantId()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId
    }

    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor with token refresh
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason?: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
        .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearTokens()
        window.location.href = '/auth/login'
        return Promise.reject(error)
      }

      try {
        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data
        setTokens({ access_token, refresh_token: newRefreshToken })

        processQueue(null, access_token)
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError as Error, null)
        clearTokens()
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api