import api from '@/lib/api'
import type { User, Tenant, AuthTokens } from '@/types'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  tenant_name: string
  tenant_slug: string
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/api/v1/auth/login', credentials)
    return response.data
  },

  async register(data: RegisterData): Promise<Tenant> {
    const response = await api.post<Tenant>('/api/v1/auth/register', data)
    return response.data
  },

  async refresh(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/api/v1/auth/logout')
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me')
    return response.data
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  async getUsers(skip = 0, limit = 100): Promise<{ items: User[]; total: number }> {
    const response = await api.get<{ items: User[]; total: number }>('/api/v1/auth/users', {
      params: { skip, limit },
    })
    return response.data
  },
}

export default authService