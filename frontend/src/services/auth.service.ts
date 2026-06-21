import api from '@/lib/api'
import axios from 'axios'
import type { LoginCredentials, AuthTokens, User } from '@/types'

// Use /api/v1 which is rewritten to Railway
const API_BASE = '/api/v1'

class AuthService {
  async login(credentials: LoginCredentials, tenantSlug?: string): Promise<AuthTokens> {
    const response = await axios.post<AuthTokens>(
      `${API_BASE}/auth/login`,
      credentials,
      {
        headers: tenantSlug ? { 'X-Tenant-Slug': tenantSlug } : {}
      }
    )
    return response.data
  }

  async getMe(): Promise<User> {
    const response = await axios.get<User>(`${API_BASE}/auth/me`, {
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
    const response = await axios.post<{ id: string }>(`${API_BASE}/auth/register`, data)
    return response.data
  }
}

export const authService = new AuthService()
export default authService
