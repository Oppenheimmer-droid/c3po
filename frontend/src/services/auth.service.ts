import api from '@/lib/api'
import axios from 'axios'
import type { LoginCredentials, AuthTokens, User } from '@/types'

const LOCAL_API = '/api'

class AuthService {
  async login(credentials: LoginCredentials, tenantSlug?: string): Promise<AuthTokens> {
    // Use local Next.js API route to proxy to Railway
    const response = await axios.post<AuthTokens>(
      `${LOCAL_API}/auth/login`,
      credentials,
      {
        headers: tenantSlug ? { 'X-Tenant-Slug': tenantSlug } : {}
      }
    )
    return response.data
  }

  async getMe(): Promise<User> {
    // Use local proxy
    const response = await axios.get<User>('/api/auth/me', {
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
    // Use local proxy
    const response = await axios.post<{ id: string }>('/api/auth/register', data)
    return response.data
  }
}

export const authService = new AuthService()
export default authService
