import api from '@/lib/api'
import type { LoginCredentials, AuthTokens } from '@/types'

class AuthService {
  async login(credentials: LoginCredentials, tenantSlug?: string): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>(
      '/auth/login',
      credentials,
      {
        headers: tenantSlug ? { 'X-Tenant-ID': tenantSlug } : {}
      }
    )

    return response.data
  }
}

export const authService = new AuthService()
