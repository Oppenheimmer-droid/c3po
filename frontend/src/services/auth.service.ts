import api from '@/lib/api'
import type { User, Tenant, AuthTokens } from '@/types'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  name: string
  slug: string
  email: string
  password: string
  first_name: string
  last_name: string
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/login', credentials)
    return response.data
  },

  async register(data: RegisterData): Promise<Tenant> {
    const response = await api.post<Tenant>('/auth/register', data)
    return response.data
  },

  async refresh(refreshToken: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  async getUsers(skip = 0, limit = 100): Promise<{ items: User[]; total: number }> {
    const response = await api.get<{ items: User[]; total: number }>('/auth/users', {
      params: { skip, limit },
    })
    return response.data
  },
}

export default authService