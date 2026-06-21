import api from '@/lib/api'
import axios from 'axios'
import type { LoginCredentials, AuthTokens, User } from '@/types'

// Use env variable for API URL - set NEXT_PUBLIC_API_URL in Vercel to Railway URL
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    return (process.env.NEXT_PUBLIC_API_URL || 'https://c3po-production-0c24.up.railway.app') + '/api/v1'
  }
  return 'https://c3po-production-0c24.up.railway.app/api/v1'
}

class AuthService {
  async login(credentials: LoginCredentials, tenantSlug?: string): Promise<AuthTokens> {
    const response = await axios.post<AuthTokens>(
      `${getApiUrl()}/auth/login`,
      credentials,
      {
        headers: tenantSlug ? { 'X-Tenant-Slug': tenantSlug } : {}
      }
    )
    return response.data
  }

  async getMe(): Promise<User> {
    const response = await axios.get<User>(`${getApiUrl()}/auth/me`, {
      headers: { Authorization: `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('c3po_access_token') : ''}` }
    })
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
    const response = await axios.post<{ id: string }>(`${getApiUrl()}/auth/register`, data)
    return response.data
  }
}

export const authService = new AuthService()
export default authService
