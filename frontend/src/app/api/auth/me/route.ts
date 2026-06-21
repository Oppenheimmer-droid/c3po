import { NextRequest, NextResponse } from 'next/server'

const RAILWAY_API = 'https://c3po-production-0c24.up.railway.app'

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    
    const response = await fetch(`${RAILWAY_API}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': authHeader || '',
        'Content-Type': 'application/json',
      },
    })
    
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json({ detail: 'Proxy error' }, { status: 500 })
  }
}
