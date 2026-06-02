import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token management
export const getAccessToken = (): string | undefined => {
  return Cookies.get('access_token')
}

export const getRefreshToken = (): string | undefined => {
  return Cookies.get('refresh_token')
}

export const setTokens = (tokens: { access_token: string; refresh_token: string }) => {
  const expiresIn = 7 // days
  Cookies.set('access_token', tokens.access_token, { expires: expiresIn, secure: true, sameSite: 'strict' })
  Cookies.set('refresh_token', tokens.refresh_token, { expires: expiresIn, secure: true, sameSite: 'strict' })
}

export const clearTokens = () => {
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
    const url = originalRequest.url || ''

    // Skip refresh for auth endpoints (prevents infinite loop)
    if (url.includes('/auth/')) {
      return Promise.reject(error)
    }

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
        // No refresh token - reject without redirecting
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
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api