import api from '@/lib/api'
import type { LoginCredentials, AuthTokens, User } from '@/types'

class AuthService {
  async login(credentials: LoginCredentials, tenantSlug?: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>(
      '/auth/login',
      credentials,
      {
        headers: tenantSlug ? { 'X-Tenant-Slug': tenantSlug } : {}
      }
    )
    return response.data
  }

  async getMe(): Promise<User> {
    const response = await api.get<User>('/api/v1/auth/me')
    return response.data
  }

  async register(data: {
    name: string
    slug: string
    email: string
    password: string
    first_name: string
    last_name: string
  }): Promise<{ id: string }> {
    const response = await api.post<{ id: string }>('/auth/register', data)
    return response.data
  }
}

export const authService = new AuthService()
export default authService
