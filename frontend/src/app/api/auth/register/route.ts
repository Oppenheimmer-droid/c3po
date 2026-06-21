import { NextRequest, NextResponse } from 'next/server'

const RAILWAY_API = 'https://c3po-production-0c24.up.railway.app'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${RAILWAY_API}/api/v1/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    const data = await response.json()
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json({ detail: 'Proxy error' }, { status: 500 })
  }
}
